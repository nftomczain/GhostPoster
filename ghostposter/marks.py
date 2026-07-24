"""Znaczniki drukowane na kafelkach: krzyże pasowania, linie cięcia,
numeracja arkuszy, linijka kontrolna 100 mm i kwadrat kalibracyjny 50x50 mm.

Współrzędne wejściowe do funkcji "per-tile" (draw_label, draw_ruler) są
lokalne dla strony docelowej (0,0 w lewym górnym rogu arkusza).
Funkcje operujące na sąsiedztwie kafelków (crosses, cutlines) same
przeliczają współrzędne absolutne strony źródłowej na lokalne każdej
z dwóch stron, żeby znacznik trafił w to samo fizyczne miejsce na obu
sklejanych arkuszach.
"""

from __future__ import annotations

from pathlib import Path

import fitz

from .geometry import Tile
from .utils import mm_to_pt

REGULAR_PATH = Path(__file__).resolve().parent / "fonts" / "DejaVuSans.ttf"
BOLD_PATH = Path(__file__).resolve().parent / "fonts" / "DejaVuSans-Bold.ttf"
REGULAR_NAME = "gp-dejavu"
BOLD_NAME = "gp-dejavu-bold"

CROSS_COLOR = (0.1, 0.3, 0.9)  # niebieski — krzyże pasowania
CUTLINE_COLOR = (0.85, 0.1, 0.1)  # czerwony — linie cięcia
INK_COLOR = (0, 0, 0)

CROSS_SIZE_PT = mm_to_pt(4)
LINE_WIDTH_PT = 0.6
MARGIN_PT = mm_to_pt(12)  # odsunięcie znaczników od krawędzi kafelka

_bold_font_measure: fitz.Font | None = None


def _bold_measure() -> fitz.Font:
    """fitz.Font do POMIARU szerokości tekstu (get_text_length nie wspiera
    niestandardowych plików czcionek, trzeba użyć obiektu Font.text_length)."""
    global _bold_font_measure
    if _bold_font_measure is None:
        _bold_font_measure = fitz.Font(fontfile=str(BOLD_PATH))
    return _bold_font_measure


def _find_tile(tiles: list[Tile], row: int, col: int) -> Tile | None:
    for t in tiles:
        if t.row == row and t.col == col:
            return t
    return None


def _draw_cross(page: fitz.Page, x: float, y: float) -> None:
    half = CROSS_SIZE_PT / 2
    page.draw_line((x - half, y), (x + half, y), color=CROSS_COLOR, width=LINE_WIDTH_PT)
    page.draw_line((x, y - half), (x, y + half), color=CROSS_COLOR, width=LINE_WIDTH_PT)
    page.draw_circle((x, y), half * 0.6, color=CROSS_COLOR, width=LINE_WIDTH_PT)


def _vertical_band(tile: Tile, neighbor: Tile) -> tuple[float, float, float] | None:
    """Wspólny pionowy pas z sąsiadem po lewej/prawej: (mid_x, y0, y1) w
    współrzędnych bezwzględnych, albo None jeśli pas jest za wąski/brak."""
    ox0, ox1 = max(tile.x0, neighbor.x0), min(tile.x1, neighbor.x1)
    oy0, oy1 = max(tile.y0, neighbor.y0), min(tile.y1, neighbor.y1)
    if ox1 <= ox0 or oy1 - oy0 <= 2 * MARGIN_PT:
        return None
    return (ox0 + ox1) / 2, oy0, oy1


def _horizontal_band(tile: Tile, neighbor: Tile) -> tuple[float, float, float] | None:
    """Wspólny poziomy pas z sąsiadem u góry/dołu: (mid_y, x0, x1) w
    współrzędnych bezwzględnych, albo None jeśli pas jest za wąski/brak."""
    ox0, ox1 = max(tile.x0, neighbor.x0), min(tile.x1, neighbor.x1)
    oy0, oy1 = max(tile.y0, neighbor.y0), min(tile.y1, neighbor.y1)
    if oy1 <= oy0 or ox1 - ox0 <= 2 * MARGIN_PT:
        return None
    return (oy0 + oy1) / 2, ox0, ox1


def draw_registration_crosses(page: fitz.Page, tile: Tile, tiles: list[Tile]) -> None:
    """Rysuje krzyże pasowania we wspólnych pasach zakładki ze WSZYSTKIMI
    sąsiadami (lewo, prawo, góra, dół), nie tylko prawym/dolnym.

    To ważne: każda para sąsiadujących arkuszy dzieli jedną fizyczną
    granicę, ale to DWA OSOBNE wydrukowane kartki papieru — obie muszą
    dostać ten sam krzyż w tym samym miejscu (przeliczony do własnych,
    lokalnych współrzędnych każdej z nich), inaczej znacznik jest
    bezużyteczny: widoczny tylko na jednej z dwóch sklejanych kartek.
    """
    for neighbor in (
        _find_tile(tiles, tile.row, tile.col + 1),
        _find_tile(tiles, tile.row, tile.col - 1),
    ):
        if neighbor is None:
            continue
        band = _vertical_band(tile, neighbor)
        if band is None:
            continue
        mid_x, y0, y1 = band
        for abs_y in (y0 + MARGIN_PT, (y0 + y1) / 2, y1 - MARGIN_PT):
            _draw_cross(page, mid_x - tile.x0, abs_y - tile.y0)

    for neighbor in (
        _find_tile(tiles, tile.row + 1, tile.col),
        _find_tile(tiles, tile.row - 1, tile.col),
    ):
        if neighbor is None:
            continue
        band = _horizontal_band(tile, neighbor)
        if band is None:
            continue
        mid_y, x0, x1 = band
        for abs_x in (x0 + MARGIN_PT, (x0 + x1) / 2, x1 - MARGIN_PT):
            _draw_cross(page, abs_x - tile.x0, mid_y - tile.y0)


def draw_cutlines(page: fitz.Page, tile: Tile, tiles: list[Tile]) -> None:
    """Rysuje przerywaną linię cięcia na środku każdego wspólnego pasa
    zakładki, ze WSZYSTKIMI sąsiadami (lewo, prawo, góra, dół) — z tego
    samego powodu co `draw_registration_crosses`: obie sklejane kartki
    muszą mieć tę linię u siebie, nie tylko jedna z nich."""
    dashes = "[3 2] 0"

    for neighbor in (
        _find_tile(tiles, tile.row, tile.col + 1),
        _find_tile(tiles, tile.row, tile.col - 1),
    ):
        if neighbor is None:
            continue
        ox0, ox1 = max(tile.x0, neighbor.x0), min(tile.x1, neighbor.x1)
        oy0, oy1 = max(tile.y0, neighbor.y0), min(tile.y1, neighbor.y1)
        if ox1 > ox0 and oy1 > oy0:
            mid_x = (ox0 + ox1) / 2 - tile.x0
            page.draw_line(
                (mid_x, oy0 - tile.y0),
                (mid_x, oy1 - tile.y0),
                color=CUTLINE_COLOR,
                width=LINE_WIDTH_PT,
                dashes=dashes,
            )

    for neighbor in (
        _find_tile(tiles, tile.row + 1, tile.col),
        _find_tile(tiles, tile.row - 1, tile.col),
    ):
        if neighbor is None:
            continue
        ox0, ox1 = max(tile.x0, neighbor.x0), min(tile.x1, neighbor.x1)
        oy0, oy1 = max(tile.y0, neighbor.y0), min(tile.y1, neighbor.y1)
        if oy1 > oy0 and ox1 > ox0:
            mid_y = (oy0 + oy1) / 2 - tile.y0
            page.draw_line(
                (ox0 - tile.x0, mid_y),
                (ox1 - tile.x0, mid_y),
                color=CUTLINE_COLOR,
                width=LINE_WIDTH_PT,
                dashes=dashes,
            )


def draw_label(page: fitz.Page, text: str) -> None:
    """Wypisuje numer arkusza (np. 'A1') w lewym górnym rogu kafelka."""
    margin = mm_to_pt(5)
    page.insert_text(
        (margin, margin + 10),
        text,
        fontsize=11,
        color=INK_COLOR,
        fontname=REGULAR_NAME,
        fontfile=str(REGULAR_PATH),
    )


def draw_do_not_scale_stamp(
    page: fitz.Page, paper_width_pt: float, overlap_pt: float = 0.0
) -> None:
    """Rysuje w prawym górnym rogu wyraźny stempel 'nie skaluj wydruku'.

    Element trybu Drukarnia. Umieszczany w obszarze zakładki (overlap_pt) —
    czyli w pasie, który i tak jest wspólny z sąsiednim arkuszem i znika
    pod klejem albo zostaje odcięty wzdłuż linii cięcia — a nie na
    obszarze właściwego rysunku, żeby nigdy nie zasłonić treści planu.

    Tekst jest dwuliniowy (węższy niż jedna długa linia), żeby lepiej
    mieścił się w wąskim pasie zakładki. Ważne: PyMuPDF po cichu ucina
    tekst, który wychodzi poza krawędź strony (insert_text nie zgłasza
    błędu, po prostu nie rysuje reszty znaków) — dlatego każda linia jest
    wyrównana do prawej względem realnej krawędzi arkusza, a jeśli nawet
    najmniejsza czytelna czcionka nie mieści się w paśmie zakładki,
    funkcja świadomie rezygnuje ze ścisłego trzymania się tego pasma na
    rzecz pokazania pełnego, nieobciętego tekstu.
    """
    lines = ["NIE SKALOWAĆ", "SKALA 100%"]
    fontsize = 7.0
    min_fontsize = 4.5
    margin = mm_to_pt(1)
    band_w = max(overlap_pt, mm_to_pt(10))

    def widest_line(fs: float) -> float:
        return max(_bold_measure().text_length(line, fontsize=fs) for line in lines)

    available = band_w - 2 * margin
    while widest_line(fontsize) > available and fontsize > min_fontsize:
        fontsize -= 0.25

    text_w = widest_line(fontsize)
    box_x1 = paper_width_pt - margin
    box_x0 = max(0.0, box_x1 - max(band_w, text_w + 2 * margin))

    line_height = fontsize * 1.2
    margin_y = mm_to_pt(2)
    box = fitz.Rect(box_x0, margin_y, box_x1, margin_y + 2 * line_height + mm_to_pt(1))
    page.draw_rect(box, color=CUTLINE_COLOR, fill=(1, 0.92, 0.92), width=0.8)

    y = margin_y + fontsize
    for line in lines:
        line_w = _bold_measure().text_length(line, fontsize=fontsize)
        x = box.x1 - margin - line_w  # wyrównanie do prawej krawędzi paska — nigdy poza stronę
        page.insert_text(
            (x, y),
            line,
            fontsize=fontsize,
            color=CUTLINE_COLOR,
            fontname=BOLD_NAME,
            fontfile=str(BOLD_PATH),
        )
        y += line_height


def draw_print_shop_info_page(page: fitz.Page, info: dict[str, str]) -> None:
    """Rysuje stronę informacyjną trybu Drukarnia z parametrami zlecenia.

    `info` to pary etykieta -> wartość, np. {"Format arkusza": "A3"}.
    Ta strona trafia jako pierwsza w wynikowym PDF, przed kafelkami.
    """
    margin = mm_to_pt(15)
    y = margin

    page.insert_text(
        (margin, y + 20),
        "KARTA ZLECENIA DRUKU",
        fontsize=18,
        color=INK_COLOR,
        fontname=BOLD_NAME,
        fontfile=str(BOLD_PATH),
    )
    y += mm_to_pt(14)

    page.insert_text(
        (margin, y + 10),
        "Wydrukować bez skalowania (skala 100%, dopasowanie do strony: WYŁĄCZONE)",
        fontsize=11,
        color=CUTLINE_COLOR,
        fontname=BOLD_NAME,
        fontfile=str(BOLD_PATH),
    )
    y += mm_to_pt(12)

    for label, value in info.items():
        page.insert_text(
            (margin, y + 6),
            f"{label}:",
            fontsize=10,
            color=INK_COLOR,
            fontname=BOLD_NAME,
            fontfile=str(BOLD_PATH),
        )
        page.insert_text(
            (margin + mm_to_pt(55), y + 6),
            str(value),
            fontsize=10,
            color=INK_COLOR,
            fontname=REGULAR_NAME,
            fontfile=str(REGULAR_PATH),
        )
        y += mm_to_pt(7)

    y += mm_to_pt(10)
    page.insert_text(
        (margin, y + 6),
        "Kolejne strony tego pliku to arkusze do wydrukowania po jednym, w podanej kolejności.",
        fontsize=9,
        color=(0.3, 0.3, 0.3),
        fontname=REGULAR_NAME,
        fontfile=str(REGULAR_PATH),
    )


def draw_ruler(page: fitz.Page, paper_height_pt: float) -> None:
    """Rysuje linijkę kontrolną 100 mm z podziałką co 10 mm oraz kwadrat
    kalibracyjny 50x50 mm w lewym dolnym rogu arkusza.

    Po wydruku odmierz linijką faktyczną długość paska — jeśli to
    dokładnie 100 mm, drukarka nie przeskalowała strony.
    """
    margin = mm_to_pt(8)
    base_y = paper_height_pt - margin

    # linijka 100 mm
    x0 = margin
    x1 = x0 + mm_to_pt(100)
    page.draw_line((x0, base_y), (x1, base_y), color=INK_COLOR, width=0.8)
    for mm in range(0, 101, 10):
        x = x0 + mm_to_pt(mm)
        tick_h = mm_to_pt(3) if mm % 50 == 0 else mm_to_pt(1.5)
        page.draw_line((x, base_y), (x, base_y - tick_h), color=INK_COLOR, width=0.6)
    page.insert_text(
        (x0, base_y - mm_to_pt(6)),
        "100 mm",
        fontsize=7,
        color=INK_COLOR,
        fontname=REGULAR_NAME,
        fontfile=str(REGULAR_PATH),
    )

    # kwadrat kalibracyjny 50x50 mm, nad linijką
    sq_size = mm_to_pt(50)
    sq_y1 = base_y - mm_to_pt(12)
    sq_y0 = sq_y1 - sq_size
    sq_rect = fitz.Rect(x0, sq_y0, x0 + sq_size, sq_y1)
    page.draw_rect(sq_rect, color=INK_COLOR, width=0.6)
    page.insert_text(
        (x0, sq_y0 - mm_to_pt(2)),
        "50x50 mm",
        fontsize=7,
        color=INK_COLOR,
        fontname=REGULAR_NAME,
        fontfile=str(REGULAR_PATH),
    )
