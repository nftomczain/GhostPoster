import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

pytest.importorskip("PySide6")

from PySide6.QtWidgets import QApplication  # noqa: E402

from ghostposter.gui import MainWindow  # noqa: E402


@pytest.fixture(scope="module")
def app():
    application = QApplication.instance() or QApplication([])
    yield application


def test_main_window_starts_with_export_disabled(app):
    window = MainWindow()
    assert window.windowTitle() == "GhostPoster"
    assert window.export_button.isEnabled() is False


def test_choosing_file_enables_export(app, tmp_path):
    window = MainWindow()
    dummy_pdf = tmp_path / "plan.pdf"
    dummy_pdf.write_bytes(b"%PDF-1.4 fake")
    window._on_file_chosen(dummy_pdf)
    assert window.export_button.isEnabled() is True


def test_real_pdf_populates_preview_with_tiles(app, tmp_path):
    import fitz

    src = tmp_path / "real.pdf"
    doc = fitz.open()
    doc.new_page(width=2000, height=1500)
    doc.save(src)
    doc.close()

    window = MainWindow()
    window._on_file_chosen(src)

    assert window.preview._base_pixmap is not None
    assert window.preview._page_size_pt is not None
    assert len(window.preview._tiles) > 0


def test_progress_signal_reaches_progress_bar(app, tmp_path, qtbot=None):
    import fitz

    src = tmp_path / "real2.pdf"
    doc = fitz.open()
    doc.new_page(width=2000, height=1500)
    doc.save(src)
    doc.close()

    window = MainWindow()
    window._on_file_chosen(src)
    window.paper_combo.setCurrentText("A4")

    seen = []
    window._worker = None  # upewniamy się, że nie ma wątku w tle z poprzedniego testu

    from ghostposter.gui import TileWorker
    from ghostposter.paper import get_paper_size_pt
    from ghostposter.tiler import plan_tiles

    paper_w, paper_h = get_paper_size_pt("A4")
    tiles = plan_tiles(src, paper_w, paper_h, overlap_mm=10, page_number=0)

    worker = TileWorker(
        input_path=src,
        output_path=tmp_path / "out.pdf",
        paper="A4",
        overlap_mm=10,
        page_number=0,
        marks=False,
        cutlines=False,
        labels=False,
    )
    worker.progress.connect(lambda done, total: seen.append((done, total)))
    worker.run()  # bez .start(), żeby test był synchroniczny i deterministyczny

    assert seen, "sygnał progress nigdy nie doszedł"
    assert seen[-1] == (len(tiles), len(tiles))


def test_settings_persist_across_windows(app):
    from PySide6.QtCore import QSettings

    # izolujemy test od realnych ustawień systemowych
    QSettings.setDefaultFormat(QSettings.IniFormat)

    window1 = MainWindow()
    window1.settings.clear()
    window1.paper_combo.setCurrentText("A2")
    window1.overlap_spin.setValue(22.0)
    window1.marks_check.setChecked(True)
    window1.maximize_check.setChecked(True)
    window1.close()  # wywołuje closeEvent -> _save_settings

    window2 = MainWindow()
    assert window2.paper_combo.currentText() == "A2"
    assert window2.overlap_spin.value() == 22.0
    assert window2.marks_check.isChecked() is True
    assert window2.maximize_check.isChecked() is True


def test_maximize_checkbox_changes_preview_orientation(app, tmp_path):
    import fitz

    src = tmp_path / "wide.pdf"
    doc = fitz.open()
    doc.new_page(width=1600, height=500)  # szeroka, niska strona
    doc.save(src)
    doc.close()

    window = MainWindow()
    window._on_file_chosen(src)
    window.paper_combo.setCurrentText("A3")
    window.overlap_spin.setValue(10)

    tiles_without = len(window.preview._tiles)
    window.maximize_check.setChecked(True)
    tiles_with = len(window.preview._tiles)

    assert tiles_with <= tiles_without


def test_language_switch_translates_static_and_dynamic_text(app, tmp_path):
    """Regresja: status na dole jest generowany dynamicznie (nie jest
    statyczna etykieta), więc samo _retranslate_ui() go nie odswieza —
    trzeba go przeliczyc ponownie po zmianie jezyka."""
    import fitz

    src = tmp_path / "plan.pdf"
    doc = fitz.open()
    doc.new_page(width=900, height=600)
    doc.save(src)
    doc.close()

    window = MainWindow()
    window._on_file_chosen(src)

    idx_en = window.language_combo.findData("en")
    window.language_combo.setCurrentIndex(idx_en)

    assert window.export_button.text().startswith("Export")
    assert "arkusz" not in window.status_label.text()
    assert "sheet" in window.status_label.text() or "Split" in window.status_label.text()
