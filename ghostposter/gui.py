"""GUI GhostPoster (v0.3) oparty o PySide6, z przełącznikiem języka PL/EN.

Uruchomienie: `ghostposter-gui` (po `pip install ghostposter[gui]`)
albo `python -m ghostposter.gui`.

Zaprojektowane pod obsługę jedną ręką i z klawiatury: każda akcja dostępna
też bez przeciągania (przycisk "Wybierz plik...", skróty klawiszowe,
strefa upuszczania aktywna też przez Enter/Spację po najechaniu Tabem),
oraz pod czytniki ekranu: wszystkie kontrolki mają ustawione accessibleName.

Zawiera podgląd strony źródłowej z nałożoną siatką podziału — aktualizuje
się automatycznie po zmianie formatu papieru, zakładki, numeru strony,
Auto Crop czy jego marginesu.

Interfejs jest dwujęzyczny (patrz `i18n.py`) — wybór języka jest
zapamiętywany między uruchomieniami razem z resztą ustawień.
"""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

import fitz  # PyMuPDF
from PySide6.QtCore import QRectF, QSettings, Qt, QThread, Signal
from PySide6.QtGui import QColor, QFont, QImage, QKeySequence, QPainter, QPen, QPixmap, QShortcut
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFileDialog,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from .blank import find_blank_tiles
from .crop import detect_content_bbox
from .geometry import Tile, compute_best_grid, compute_grid, translate_tiles
from .i18n import DEFAULT_LANG, t
from .paper import available_sizes, get_paper_size_pt
from .tiler import PageNumberOutOfRangeError, get_page_size_pt
from .utils import mm_to_pt, pt_to_mm
from .writer import write_tiled_pdf

PREVIEW_RENDER_MAX_PX = 900  # rozdzielczość renderowanej strony (niezależna od rozmiaru okna)
TILE_COLORS = [
    QColor(47, 111, 235, 200),
    QColor(219, 68, 55, 200),
    QColor(15, 157, 88, 200),
    QColor(244, 160, 0, 200),
]
CROP_MARGIN_OPTIONS_MM = [0, 2, 5, 10, 20]
DEFAULT_CROP_MARGIN_MM = 5


class DropZone(QFrame):
    """Strefa upuszczania PDF — obsługuje też klik i Enter/Spację (bez myszy)."""

    file_chosen = Signal(Path)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.lang = DEFAULT_LANG
        self.setAcceptDrops(True)
        self.setFrameShape(QFrame.StyledPanel)
        self.setMinimumHeight(80)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setStyleSheet(
            "DropZone { border: 2px dashed #888; border-radius: 8px; }"
            "DropZone:focus { border-color: #2f6feb; }"
        )

        layout = QVBoxLayout(self)
        self._label = QLabel(self)
        self._label.setAlignment(Qt.AlignCenter)
        font = self._label.font()
        font.setPointSize(font.pointSize() + 2)
        self._label.setFont(font)
        layout.addWidget(self._label)
        self._chosen_path: Path | None = None
        self.retranslate(self.lang)

    def retranslate(self, lang: str) -> None:
        self.lang = lang
        self.setAccessibleName(t(lang, "drop_zone_accessible_name"))
        self.setAccessibleDescription(t(lang, "drop_zone_accessible_desc"))
        if self._chosen_path is not None:
            self._label.setText(t(lang, "drop_zone_chosen", name=self._chosen_path.name))
        else:
            self._label.setText(t(lang, "drop_zone_text"))

    def dragEnterEvent(self, event) -> None:  # noqa: ANN001
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event) -> None:  # noqa: ANN001
        urls = event.mimeData().urls()
        if urls:
            path = Path(urls[0].toLocalFile())
            if path.suffix.lower() == ".pdf":
                self.set_file(path)
            else:
                QMessageBox.warning(
                    self, t(self.lang, "bad_file_title"), t(self.lang, "bad_file_body")
                )

    def mousePressEvent(self, event) -> None:  # noqa: ANN001
        self._browse()

    def keyPressEvent(self, event) -> None:  # noqa: ANN001
        if event.key() in (Qt.Key_Return, Qt.Key_Enter, Qt.Key_Space):
            self._browse()
        else:
            super().keyPressEvent(event)

    def _browse(self) -> None:
        path_str, _ = QFileDialog.getOpenFileName(
            self, t(self.lang, "choose_pdf_dialog"), "", "PDF (*.pdf)"
        )
        if path_str:
            self.set_file(Path(path_str))

    def set_file(self, path: Path) -> None:
        self._chosen_path = path
        self._label.setText(t(self.lang, "drop_zone_chosen", name=path.name))
        self.file_chosen.emit(path)


class PreviewWidget(QWidget):
    """Podgląd strony źródłowej z nałożoną siatką podziału na arkusze.

    Renderowanie strony (kosztowne) i przeliczanie siatki (tanie) są
    rozdzielone: `set_source_page` robi jedno i drugie, `set_tiles`
    tylko odświeża nałożoną siatkę bez ponownego renderowania PDF.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.lang = DEFAULT_LANG
        self.setMinimumSize(320, 320)
        self._base_pixmap: QPixmap | None = None
        self._page_size_pt: tuple[float, float] | None = None
        self._tiles: list[Tile] = []
        self.retranslate(self.lang)

    def retranslate(self, lang: str) -> None:
        self.lang = lang
        self.setAccessibleName(t(lang, "preview_accessible_name"))
        self.update()

    def clear(self) -> None:
        self._base_pixmap = None
        self._page_size_pt = None
        self._tiles = []
        self.update()

    def set_source_page(self, input_path: Path, page_number: int) -> tuple[float, float]:
        """Renderuje wskazaną stronę PDF i zwraca jej rozmiar w punktach."""
        with fitz.open(input_path) as doc:
            page = doc[page_number]
            rect = page.rect
            scale = PREVIEW_RENDER_MAX_PX / max(rect.width, rect.height)
            pix = page.get_pixmap(matrix=fitz.Matrix(scale, scale))
            img = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format_RGB888)
            self._base_pixmap = QPixmap.fromImage(img.copy())
            self._page_size_pt = (rect.width, rect.height)
        self._tiles = []
        self.update()
        return self._page_size_pt

    def set_tiles(self, tiles: list[Tile]) -> None:
        self._tiles = tiles
        self.update()

    def paintEvent(self, event) -> None:  # noqa: ANN001
        painter = QPainter(self)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        painter.fillRect(self.rect(), QColor("#f2f2f2"))

        if self._base_pixmap is None or self._page_size_pt is None:
            painter.setPen(QColor("#666"))
            painter.setFont(QFont(painter.font().family(), 10))
            painter.drawText(self.rect(), Qt.AlignCenter, t(self.lang, "preview_placeholder"))
            painter.end()
            return

        page_w_pt, page_h_pt = self._page_size_pt
        widget_w, widget_h = self.width(), self.height()
        scale = min(widget_w / page_w_pt, widget_h / page_h_pt)
        draw_w, draw_h = page_w_pt * scale, page_h_pt * scale
        offset_x, offset_y = (widget_w - draw_w) / 2, (widget_h - draw_h) / 2

        target = QRectF(offset_x, offset_y, draw_w, draw_h)
        painter.drawPixmap(target, self._base_pixmap, QRectF(self._base_pixmap.rect()))

        for tile in self._tiles:
            color = TILE_COLORS[(tile.row + tile.col) % len(TILE_COLORS)]
            pen = QPen(color, 2)
            painter.setPen(pen)
            rect = QRectF(
                offset_x + tile.x0 * scale,
                offset_y + tile.y0 * scale,
                tile.width * scale,
                tile.height * scale,
            )
            painter.drawRect(rect)
            painter.setPen(QColor(color.red(), color.green(), color.blue(), 255))
            painter.drawText(rect.adjusted(3, 2, 0, 0), Qt.AlignLeft | Qt.AlignTop, tile.label)

        painter.end()


class TileWorker(QThread):
    """Wykonuje planowanie i zapis w osobnym wątku, żeby nie blokować GUI.

    Emituje wyniki jako dane strukturalne (liczby, ścieżki), nie gotowe
    zdania — tekst do wyświetlenia składa MainWindow przez `i18n.t()`,
    dzięki czemu worker nie musi nic wiedzieć o aktualnym języku GUI.
    """

    finished_ok = Signal(int, int, str)  # (zapisane, pominięte_puste, output_path)
    failed = Signal(str)
    progress = Signal(int, int)  # (gotowe, razem)

    def __init__(
        self,
        input_path: Path,
        output_path: Path,
        paper: str,
        overlap_mm: float,
        page_number: int,
        marks: bool,
        cutlines: bool,
        labels: bool,
        maximize: bool = False,
        print_shop: bool = False,
        skip_blank: bool = False,
        auto_crop: bool = False,
        crop_margin_mm: float = DEFAULT_CROP_MARGIN_MM,
    ) -> None:
        super().__init__()
        self.input_path = input_path
        self.output_path = output_path
        self.paper = paper
        self.overlap_mm = overlap_mm
        self.page_number = page_number
        self.marks = marks
        self.cutlines = cutlines
        self.labels = labels
        self.maximize = maximize
        self.print_shop = print_shop
        self.skip_blank = skip_blank
        self.auto_crop = auto_crop
        self.crop_margin_mm = crop_margin_mm

    def run(self) -> None:
        try:
            paper_w_pt, paper_h_pt = get_paper_size_pt(self.paper)
            page_w_pt, page_h_pt = get_page_size_pt(self.input_path, self.page_number)
            overlap_pt = mm_to_pt(self.overlap_mm)

            effective_w_pt, effective_h_pt = page_w_pt, page_h_pt
            offset_x, offset_y = 0.0, 0.0
            if self.auto_crop:
                bbox = detect_content_bbox(
                    self.input_path, self.page_number, padding_mm=self.crop_margin_mm
                )
                effective_w_pt, effective_h_pt = bbox.width, bbox.height
                offset_x, offset_y = bbox.x0, bbox.y0

            if self.maximize:
                result = compute_best_grid(
                    effective_w_pt, effective_h_pt, paper_w_pt, paper_h_pt, overlap_pt
                )
                tiles = result.tiles
                paper_w_pt, paper_h_pt = result.paper_width_pt, result.paper_height_pt
            else:
                tiles = compute_grid(
                    effective_w_pt, effective_h_pt, paper_w_pt, paper_h_pt, overlap_pt
                )

            if offset_x or offset_y:
                tiles = translate_tiles(tiles, offset_x, offset_y)

            skip_labels: set[str] = set()
            if self.skip_blank:
                blanks = find_blank_tiles(self.input_path, tiles, self.page_number)
                skip_labels = {t.label for t in blanks}

            print_shop_info = None
            if self.print_shop:
                print_shop_info = {
                    "Plik źródłowy": self.input_path.name,
                    "Strona źródłowa": str(self.page_number),
                    "Format arkusza": self.paper,
                    "Orientacja": "poziomo" if paper_w_pt > paper_h_pt else "pionowo",
                    "Zakładka": f"{self.overlap_mm:.1f} mm",
                    "Liczba arkuszy": str(len(tiles) - len(skip_labels)),
                    "Rozmiar arkusza": (
                        f"{pt_to_mm(paper_w_pt):.0f} x {pt_to_mm(paper_h_pt):.0f} mm"
                    ),
                    "Skala": "100% (bez przeskalowania)",
                    "Data wygenerowania": date.today().isoformat(),
                }

            write_tiled_pdf(
                input_path=self.input_path,
                output_path=self.output_path,
                tiles=tiles,
                paper_width_pt=paper_w_pt,
                paper_height_pt=paper_h_pt,
                page_number=self.page_number,
                draw_marks=self.marks,
                draw_cutlines=self.cutlines,
                draw_labels=self.labels,
                print_shop=self.print_shop,
                print_shop_info=print_shop_info,
                overlap_pt=overlap_pt,
                skip_labels=skip_labels,
                progress_callback=lambda done, total: self.progress.emit(done, total),
            )
            written = len(tiles) - len(skip_labels)
            self.finished_ok.emit(written, len(skip_labels), str(self.output_path))
        except Exception as exc:  # noqa: BLE001
            self.failed.emit(str(exc))


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.lang = DEFAULT_LANG
        self.setWindowTitle(t(self.lang, "window_title"))
        self.resize(560, 680)
        self._input_path: Path | None = None
        self._page_size_pt: tuple[float, float] | None = None
        self._content_bbox_pt: fitz.Rect | None = None
        self._worker: TileWorker | None = None

        central = QWidget(self)
        self.setCentralWidget(central)
        root = QVBoxLayout(central)

        lang_row = QHBoxLayout()
        lang_row.addStretch(1)
        self.language_label = QLabel(self)
        lang_row.addWidget(self.language_label)
        self.language_combo = QComboBox(self)
        self.language_combo.addItem("Polski", userData="pl")
        self.language_combo.addItem("English", userData="en")
        self.language_combo.currentIndexChanged.connect(self._on_language_changed)
        lang_row.addWidget(self.language_combo)
        root.addLayout(lang_row)

        self.drop_zone = DropZone(self)
        self.drop_zone.file_chosen.connect(self._on_file_chosen)
        root.addWidget(self.drop_zone)

        self.preview = PreviewWidget(self)
        root.addWidget(self.preview, stretch=1)

        form = QFormLayout()

        self.paper_combo = QComboBox(self)
        self.paper_combo.addItems(available_sizes())
        self.paper_combo.setCurrentText("A3")
        self.paper_combo.currentTextChanged.connect(self._recompute_tiles)
        self.paper_label = QLabel(self)
        form.addRow(self.paper_label, self.paper_combo)

        self.overlap_spin = QDoubleSpinBox(self)
        self.overlap_spin.setRange(0, 50)
        self.overlap_spin.setValue(10)
        self.overlap_spin.setSuffix(" mm")
        self.overlap_spin.valueChanged.connect(self._recompute_tiles)
        self.overlap_label = QLabel(self)
        form.addRow(self.overlap_label, self.overlap_spin)

        self.page_spin = QSpinBox(self)
        self.page_spin.setRange(0, 9999)
        self.page_spin.valueChanged.connect(self._on_page_changed)
        self.page_label = QLabel(self)
        form.addRow(self.page_label, self.page_spin)

        self.crop_margin_combo = QComboBox(self)
        for mm in CROP_MARGIN_OPTIONS_MM:
            self.crop_margin_combo.addItem(f"{mm} mm", userData=mm)
        self.crop_margin_combo.setCurrentIndex(CROP_MARGIN_OPTIONS_MM.index(DEFAULT_CROP_MARGIN_MM))
        self.crop_margin_combo.currentIndexChanged.connect(self._on_crop_margin_changed)
        self.crop_margin_label = QLabel(self)
        form.addRow(self.crop_margin_label, self.crop_margin_combo)

        root.addLayout(form)

        checks = QHBoxLayout()
        self.marks_check = QCheckBox(self)
        self.cutlines_check = QCheckBox(self)
        self.labels_check = QCheckBox(self)
        self.maximize_check = QCheckBox(self)
        self.auto_crop_check = QCheckBox(self)
        for cb in (
            self.marks_check,
            self.cutlines_check,
            self.labels_check,
            self.maximize_check,
            self.auto_crop_check,
        ):
            checks.addWidget(cb)
        self.maximize_check.toggled.connect(self._recompute_tiles)
        self.auto_crop_check.toggled.connect(self._on_auto_crop_toggled)
        root.addLayout(checks)

        self.print_shop_check = QCheckBox(self)
        self.print_shop_check.setStyleSheet("QCheckBox { font-weight: bold; }")
        root.addWidget(self.print_shop_check)

        self.skip_blank_check = QCheckBox(self)
        root.addWidget(self.skip_blank_check)

        self.export_button = QPushButton(self)
        self.export_button.setEnabled(False)
        self.export_button.clicked.connect(self._on_export)
        root.addWidget(self.export_button)

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setVisible(False)
        root.addWidget(self.progress_bar)

        self.status_label = QLabel("", self)
        self.status_label.setWordWrap(True)
        self.status_label.setAccessibleName("Status")
        root.addWidget(self.status_label)

        QShortcut(QKeySequence("Ctrl+O"), self, activated=self.drop_zone._browse)
        QShortcut(QKeySequence("Ctrl+E"), self, activated=self._on_export)

        self.settings = QSettings("GhostPoster", "GhostPoster")
        self._load_settings()
        self._retranslate_ui()

    # -- język -----------------------------------------------------------

    def _on_language_changed(self, _index: int) -> None:
        self.lang = self.language_combo.currentData()
        self._retranslate_ui()
        # _retranslate_ui() aktualizuje tylko statyczne napisy (przyciski,
        # checkboxy); status na dole jest generowany dynamicznie i trzeba
        # go przeliczyć ponownie, żeby też zmienił język
        if self._page_size_pt is not None:
            self._recompute_tiles()
        elif self._input_path is not None:
            self.status_label.setText(t(self.lang, "status_ready", path=self._input_path))

    def _retranslate_ui(self) -> None:
        lang = self.lang
        self.setWindowTitle(t(lang, "window_title"))
        self.language_label.setText(t(lang, "language_label"))

        self.drop_zone.retranslate(lang)
        self.preview.retranslate(lang)

        self.paper_label.setText(t(lang, "paper_label"))
        self.paper_combo.setAccessibleName(t(lang, "paper_accessible_name"))
        self.overlap_label.setText(t(lang, "overlap_label"))
        self.overlap_spin.setAccessibleName(t(lang, "overlap_accessible_name"))
        self.page_label.setText(t(lang, "page_label"))
        self.page_spin.setAccessibleName(t(lang, "page_accessible_name"))
        self.crop_margin_label.setText(t(lang, "crop_margin_label"))
        self.crop_margin_combo.setAccessibleName(t(lang, "crop_margin_accessible_name"))

        self.marks_check.setText(t(lang, "marks_check"))
        self.marks_check.setAccessibleName(t(lang, "marks_check"))
        self.cutlines_check.setText(t(lang, "cutlines_check"))
        self.cutlines_check.setAccessibleName(t(lang, "cutlines_check"))
        self.labels_check.setText(t(lang, "labels_check"))
        self.labels_check.setAccessibleName(t(lang, "labels_check"))
        self.maximize_check.setText(t(lang, "maximize_check"))
        self.maximize_check.setAccessibleName(t(lang, "maximize_check"))
        self.auto_crop_check.setText(t(lang, "auto_crop_check"))
        self.auto_crop_check.setAccessibleName(t(lang, "auto_crop_check"))
        self.print_shop_check.setText(t(lang, "print_shop_check"))
        self.print_shop_check.setAccessibleName(t(lang, "print_shop_check"))
        self.skip_blank_check.setText(t(lang, "skip_blank_check"))
        self.skip_blank_check.setAccessibleName(t(lang, "skip_blank_check"))

        self.export_button.setText(t(lang, "export_button"))
        self.export_button.setAccessibleName(t(lang, "export_accessible_name"))
        self.progress_bar.setAccessibleName(t(lang, "progress_accessible_name"))

    # -- zapamiętane ustawienia ----------------------------------------

    def _load_settings(self) -> None:
        """Przywraca ostatnio użyte ustawienia (format, zakładka, znaczniki, język)."""
        lang = self.settings.value("language", DEFAULT_LANG, type=str)
        idx = self.language_combo.findData(lang)
        self.language_combo.setCurrentIndex(idx if idx >= 0 else 0)
        self.lang = self.language_combo.currentData()

        paper = self.settings.value("paper", "A3", type=str)
        if paper in available_sizes():
            self.paper_combo.setCurrentText(paper)
        self.overlap_spin.setValue(self.settings.value("overlap_mm", 10.0, type=float))
        self.marks_check.setChecked(self.settings.value("marks", False, type=bool))
        self.cutlines_check.setChecked(self.settings.value("cutlines", False, type=bool))
        self.labels_check.setChecked(self.settings.value("labels", False, type=bool))
        self.maximize_check.setChecked(self.settings.value("maximize", False, type=bool))
        self.print_shop_check.setChecked(self.settings.value("print_shop", False, type=bool))
        self.skip_blank_check.setChecked(self.settings.value("skip_blank", False, type=bool))
        self.auto_crop_check.setChecked(self.settings.value("auto_crop", False, type=bool))

        crop_margin = self.settings.value("crop_margin_mm", DEFAULT_CROP_MARGIN_MM, type=int)
        idx = self.crop_margin_combo.findData(crop_margin)
        self.crop_margin_combo.setCurrentIndex(
            idx if idx >= 0 else CROP_MARGIN_OPTIONS_MM.index(DEFAULT_CROP_MARGIN_MM)
        )

    def _save_settings(self) -> None:
        self.settings.setValue("language", self.language_combo.currentData())
        self.settings.setValue("paper", self.paper_combo.currentText())
        self.settings.setValue("overlap_mm", self.overlap_spin.value())
        self.settings.setValue("marks", self.marks_check.isChecked())
        self.settings.setValue("cutlines", self.cutlines_check.isChecked())
        self.settings.setValue("labels", self.labels_check.isChecked())
        self.settings.setValue("maximize", self.maximize_check.isChecked())
        self.settings.setValue("print_shop", self.print_shop_check.isChecked())
        self.settings.setValue("skip_blank", self.skip_blank_check.isChecked())
        self.settings.setValue("auto_crop", self.auto_crop_check.isChecked())
        self.settings.setValue("crop_margin_mm", self.crop_margin_combo.currentData())

    def closeEvent(self, event) -> None:  # noqa: ANN001
        self._save_settings()
        super().closeEvent(event)

    # -- podgląd -----------------------------------------------------

    def _on_file_chosen(self, path: Path) -> None:
        self._input_path = path
        self._content_bbox_pt = None
        self.page_spin.blockSignals(True)
        self.page_spin.setValue(0)
        self.page_spin.blockSignals(False)
        self.export_button.setEnabled(True)
        self._reload_preview_source()

    def _on_page_changed(self, _value: int) -> None:
        if self._input_path is not None:
            self._content_bbox_pt = None
            self._reload_preview_source()

    def _on_auto_crop_toggled(self, _checked: bool) -> None:
        self._recompute_tiles()

    def _on_crop_margin_changed(self, _index: int) -> None:
        self._content_bbox_pt = None
        if self.auto_crop_check.isChecked():
            self._recompute_tiles()

    def _reload_preview_source(self) -> None:
        """Renderuje wybraną stronę PDF od nowa (plik lub numer strony się zmienił)."""
        if self._input_path is None:
            return
        try:
            self._page_size_pt = self.preview.set_source_page(
                self._input_path, self.page_spin.value()
            )
            self.status_label.setText(t(self.lang, "status_ready", path=self._input_path))
        except PageNumberOutOfRangeError as exc:
            self._page_size_pt = None
            self.preview.clear()
            self.status_label.setText(str(exc))
            return
        except Exception as exc:  # noqa: BLE001
            self._page_size_pt = None
            self.preview.clear()
            self.status_label.setText(t(self.lang, "status_page_error", error=exc))
            return
        self._recompute_tiles()

    def _recompute_tiles(self, *_args) -> None:
        """Przelicza tylko siatkę podziału na podstawie już wyrenderowanej strony."""
        if self._page_size_pt is None:
            return
        try:
            paper_w_pt, paper_h_pt = get_paper_size_pt(self.paper_combo.currentText())
        except Exception:  # noqa: BLE001
            return

        crop_note = ""
        offset_x, offset_y = 0.0, 0.0
        if self.auto_crop_check.isChecked():
            if self._content_bbox_pt is None:
                try:
                    self._content_bbox_pt = detect_content_bbox(
                        self._input_path,
                        self.page_spin.value(),
                        padding_mm=self.crop_margin_combo.currentData(),
                    )
                except Exception as exc:  # noqa: BLE001
                    self.status_label.setText(t(self.lang, "status_auto_crop_failed", error=exc))
                    self.auto_crop_check.setChecked(False)
                    return
            bbox = self._content_bbox_pt
            page_w_pt, page_h_pt = bbox.width, bbox.height
            offset_x, offset_y = bbox.x0, bbox.y0
            crop_note = t(self.lang, "status_crop_note")
        else:
            page_w_pt, page_h_pt = self._page_size_pt

        overlap_pt = mm_to_pt(self.overlap_spin.value())
        try:
            if self.maximize_check.isChecked():
                result = compute_best_grid(page_w_pt, page_h_pt, paper_w_pt, paper_h_pt, overlap_pt)
                tiles = result.tiles
                orientation_key = (
                    "orientation_landscape"
                    if result.orientation == "poziomo"
                    else "orientation_portrait"
                )
                note = t(
                    self.lang,
                    "status_orientation_note",
                    orientation=t(self.lang, orientation_key),
                )
            else:
                tiles = compute_grid(page_w_pt, page_h_pt, paper_w_pt, paper_h_pt, overlap_pt)
                note = ""
        except ValueError as exc:
            self.status_label.setText(str(exc))
            return

        if offset_x or offset_y:
            tiles = translate_tiles(tiles, offset_x, offset_y)

        self.preview.set_tiles(tiles)
        base = t(self.lang, "status_split", count=len(tiles), paper=self.paper_combo.currentText())
        self.status_label.setText(f"{base}{note}{crop_note}")

    # -- eksport -------------------------------------------------------

    def _on_export(self) -> None:
        if self._input_path is None:
            QMessageBox.information(
                self, t(self.lang, "no_file_title"), t(self.lang, "no_file_body")
            )
            return

        default_out = self._input_path.with_name(f"{self._input_path.stem}_tiled.pdf")
        out_str, _ = QFileDialog.getSaveFileName(
            self, t(self.lang, "save_as_dialog"), str(default_out), "PDF (*.pdf)"
        )
        if not out_str:
            return

        self.export_button.setEnabled(False)
        self.status_label.setText(t(self.lang, "status_processing"))
        self.progress_bar.setRange(0, 1)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)

        self._worker = TileWorker(
            input_path=self._input_path,
            output_path=Path(out_str),
            paper=self.paper_combo.currentText(),
            overlap_mm=self.overlap_spin.value(),
            page_number=self.page_spin.value(),
            marks=self.marks_check.isChecked(),
            cutlines=self.cutlines_check.isChecked(),
            labels=self.labels_check.isChecked(),
            maximize=self.maximize_check.isChecked(),
            print_shop=self.print_shop_check.isChecked(),
            skip_blank=self.skip_blank_check.isChecked(),
            auto_crop=self.auto_crop_check.isChecked(),
            crop_margin_mm=self.crop_margin_combo.currentData(),
        )
        self._worker.progress.connect(self._on_progress)
        self._worker.finished_ok.connect(self._on_success)
        self._worker.failed.connect(self._on_error)
        self._worker.start()

    def _on_progress(self, done: int, total: int) -> None:
        self.progress_bar.setRange(0, total)
        self.progress_bar.setValue(done)
        self.status_label.setText(t(self.lang, "status_progress", done=done, total=total))

    def _on_success(self, written: int, skipped: int, output_path: str) -> None:
        self.export_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        base = t(self.lang, "status_saved", count=written, path=output_path)
        skipped_note = t(self.lang, "status_saved_skipped", count=skipped) if skipped else ""
        self.status_label.setText(f"{base}{skipped_note}")

    def _on_error(self, message: str) -> None:
        self.export_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.status_label.setText(t(self.lang, "status_error", message=message))
        QMessageBox.critical(self, t(self.lang, "error_title"), message)


def main() -> None:
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
