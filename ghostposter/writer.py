"""Renderuje zaplanowane kafelki do nowego pliku PDF, jeden kafelek = jedna strona.

Każda nowa strona ma dokładnie rozmiar docelowego formatu papieru (np. A3),
a fragment strony źródłowej jest wklejany w skali 1:1 (bez przeskalowania),
zaczynając od lewego górnego rogu. Opcjonalnie dorysowywane są znaczniki
z modułu `marks`: krzyże pasowania, linie cięcia, numeracja i linijka
kontrolna. Puste kafelki (patrz `blank.py`) mogą być pominięte, żeby nie
drukować niepotrzebnych arkuszy.

O STRONACH Z ROTACJĄ (`page.rotation != 0` — typowe dla dużych/zeskanowanych
planów, gdzie strona jest fizycznie zapisana w pionie, a wyświetlana obrócona
do poziomu):

`Page.show_pdf_page(clip=...)` po cichu gubi treść dla fragmentów oddalonych
od rogu strony na takich stronach — sprawdzone bezpośrednio na realnym
pliku użytkownika. Próbowaliśmy naprawić to przeliczając `clip` przez
`page.derotation_matrix` — na jednym kontrolowanym przykładzie dało to
wynik piksel w piksel identyczny z niezależnym rendererem, ale na kolejnych
przykładach (i na docelowym pliku, który ma dodatkowo przesunięty `cropbox`
względem `mediabox`) ta sama poprawka rzucała `ValueError: clip must be
finite and not empty` — okazało się, że oczekiwany układ współrzędnych
`clip` nie jest spójny między przypadkami w sposób, który dałoby się
niezawodnie przewidzieć.

`Page.get_pixmap(clip=...)` natomiast działał POPRAWNIE w każdym
przetestowanym przypadku (zweryfikowane wielokrotnie względem niezależnie
wyliczonej wartości referencyjnej). Dlatego dla stron z rotacją kafelki są
rasteryzowane (renderowane jako obraz w rozdzielczości `_ROTATED_PAGE_DPI`,
kompresowane do PNG) zamiast kopiowane wektorowo — kosztem utraty
nieskończonej skalowalności i większego rozmiaru pliku, ale z pewnością,
że treść się nie gubi. Jeśli w przyszłości znajdzie się niezawodna
wektorowa poprawka dla `show_pdf_page`, ta funkcja to jedyne miejsce,
które trzeba by zmienić.
"""

from __future__ import annotations

import io
from collections.abc import Callable
from pathlib import Path

import fitz  # PyMuPDF
from PIL import Image

from . import __version__, marks
from .debug import export_info, pdf_info
from .geometry import Tile

ProgressCallback = Callable[[int, int], None]

# Rozdzielczość rasteryzacji kafelków dla stron z rotacją (patrz docstring
# modułu) — 200 DPI to nadal bardzo dobra jakość druku, a plik wynikowy
# zostaje rozsądnych rozmiarów nawet dla bardzo dużych planów.
_ROTATED_PAGE_DPI = 200
# Próg progowania do czystej czerni/bieli (0-255) — rysunki techniczne to
# w praktyce zawsze czarna kreska na białym tle, więc 1-bit PNG zamiast
# skali szarości daje ~10x mniejszy plik bez zauważalnej utraty jakości.
_BILEVEL_THRESHOLD = 200


def _rasterize_tile_png(source_page: fitz.Page, clip_rect: fitz.Rect, scale: float) -> bytes:
    """Renderuje wycinek strony i zwraca skompresowany PNG 1-bit (czerń/biel)."""
    pix = source_page.get_pixmap(
        clip=clip_rect, matrix=fitz.Matrix(scale, scale), colorspace=fitz.csGRAY
    )
    img = Image.frombytes("L", (pix.width, pix.height), pix.samples)
    bilevel = img.point(lambda p: 0 if p < _BILEVEL_THRESHOLD else 255, mode="1")
    buf = io.BytesIO()
    bilevel.save(buf, format="PNG")
    return buf.getvalue()


def write_tiled_pdf(
    input_path: Path,
    output_path: Path,
    tiles: list[Tile],
    paper_width_pt: float,
    paper_height_pt: float,
    page_number: int = 0,
    draw_marks: bool = False,
    draw_cutlines: bool = False,
    draw_labels: bool = False,
    print_shop: bool = False,
    print_shop_info: dict[str, str] | None = None,
    overlap_pt: float = 0.0,
    skip_labels: set[str] | None = None,
    progress_callback: ProgressCallback | None = None,
) -> list[str]:
    """Zapisuje listę kafelków jako osobne strony nowego pliku PDF.

    Args:
        input_path: ścieżka do źródłowego PDF.
        output_path: ścieżka pliku wynikowego.
        tiles: lista kafelków wyliczona przez `tiler.plan_tiles`.
        paper_width_pt: szerokość docelowego arkusza w punktach.
        paper_height_pt: wysokość docelowego arkusza w punktach.
        page_number: numer strony źródłowej (0-based) do podziału.
        draw_marks: dorysuj krzyże pasowania na wspólnych zakładkach.
        draw_cutlines: dorysuj linie cięcia na wspólnych zakładkach.
        draw_labels: dorysuj numerację arkusza, linijkę 100 mm i kwadrat 50x50 mm.
        print_shop: tryb Drukarnia — stempel "nie skaluj" na każdym arkuszu
            plus strona informacyjna z parametrami zlecenia na początku pliku.
        print_shop_info: pary etykieta -> wartość do strony informacyjnej
            (np. {"Plik źródłowy": "plan.pdf", "Format arkusza": "A3"}).
            Wymagane, jeśli `print_shop=True`.
        overlap_pt: szerokość zakładki w punktach — używana do umieszczenia
            stempla trybu Drukarnia w obszarze zakładki, a nie na rysunku.
        skip_labels: etykiety kafelków (np. {"D1", "D2"}) do pominięcia —
            zwykle puste marginesy wykryte przez `blank.find_blank_tiles`.
        progress_callback: wywoływany po każdym rozpatrzonym kafelku (także
            pominiętym) jako `callback(ile_gotowych, ile_razem)`.

    Returns:
        Lista etykiet kafelków faktycznie pominiętych podczas zapisu.
    """
    total = len(tiles)
    input_path = Path(input_path)
    output_path = Path(output_path)
    skip_labels = skip_labels or set()
    actually_skipped: list[str] = []

    with fitz.open(input_path) as src, fitz.open() as out:
        source_page = src[page_number]
        use_raster = source_page.rotation != 0

        pdf_info(input_path, src, page_number)
        export_info(input_path, output_path, tiles)

        if print_shop:
            info_page = out.new_page(width=paper_width_pt, height=paper_height_pt)
            marks.draw_print_shop_info_page(info_page, print_shop_info or {})

        for index, tile in enumerate(tiles, start=1):
            if tile.label in skip_labels:
                actually_skipped.append(tile.label)
            else:
                new_page = out.new_page(width=paper_width_pt, height=paper_height_pt)
                clip_rect = fitz.Rect(tile.x0, tile.y0, tile.x1, tile.y1)
                target_rect = fitz.Rect(0, 0, tile.width, tile.height)

                if use_raster:
                    scale = _ROTATED_PAGE_DPI / 72
                    png_bytes = _rasterize_tile_png(source_page, clip_rect, scale)
                    new_page.insert_image(target_rect, stream=png_bytes)
                else:
                    new_page.show_pdf_page(target_rect, src, page_number, clip=clip_rect)

                if draw_marks:
                    marks.draw_registration_crosses(new_page, tile, tiles)
                if draw_cutlines:
                    marks.draw_cutlines(new_page, tile, tiles)
                if draw_labels:
                    marks.draw_label(new_page, tile.label)
                    marks.draw_ruler(new_page, paper_height_pt)
                if print_shop:
                    marks.draw_do_not_scale_stamp(new_page, paper_width_pt, overlap_pt)

            if progress_callback is not None:
                progress_callback(index, total)

        out.set_metadata(
            {
                "title": "GhostPoster Export",
                "creator": f"GhostPoster {__version__}",
                "producer": "GhostPoster",
            }
        )

        output_path.parent.mkdir(parents=True, exist_ok=True)
        out.save(output_path)

    return actually_skipped
