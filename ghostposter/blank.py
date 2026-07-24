"""Wykrywanie kafelków, które po podziale wyszłyby praktycznie puste
(np. sam margines strony źródłowej) — żeby nie drukować niepotrzebnych
arkuszy.

Detekcja jest celowo tania: renderujemy każdy kafelek w bardzo niskiej
rozdzielczości (rząd 80px na dłuższym boku) i liczymy, jaki ułamek
pikseli nie jest biały. To wystarcza, żeby odróżnić "pusty margines"
od "tu jest fragment rysunku", a jest wielokrotnie szybsze niż
renderowanie w pełnej rozdzielczości.
"""

from __future__ import annotations

from pathlib import Path

import fitz

from .geometry import Tile

_SAMPLE_MAX_PX = 80
_WHITE_THRESHOLD = 250  # bajt >= tego uznajemy za "biały" (skala szarości 0-255)


def tile_ink_fraction(doc: fitz.Document, page_number: int, tile: Tile) -> float:
    """Zwraca ułamek pikseli kafelka, które NIE są białe (0.0 = całkiem pusty)."""
    page = doc[page_number]
    clip = fitz.Rect(tile.x0, tile.y0, tile.x1, tile.y1)
    longest_side = max(tile.width, tile.height, 1e-6)
    scale = min(_SAMPLE_MAX_PX / longest_side, 2.0)
    scale = max(scale, 0.02)

    pix = page.get_pixmap(clip=clip, matrix=fitz.Matrix(scale, scale), colorspace=fitz.csGRAY)
    data = pix.samples
    if not data:
        return 0.0
    nonwhite = sum(1 for byte in data if byte < _WHITE_THRESHOLD)
    return nonwhite / len(data)


def find_blank_tiles(
    input_path: Path,
    tiles: list[Tile],
    page_number: int,
    ink_threshold: float = 0.005,
) -> list[Tile]:
    """Zwraca podzbiór `tiles`, które są praktycznie puste (poniżej `ink_threshold`).

    `ink_threshold=0.005` oznacza: jeśli mniej niż 0.5% pikseli kafelka ma
    jakikolwiek ślad treści, uznajemy go za pusty margines, nie fragment
    rysunku.
    """
    blanks: list[Tile] = []
    with fitz.open(input_path) as doc:
        for tile in tiles:
            if tile_ink_fraction(doc, page_number, tile) < ink_threshold:
                blanks.append(tile)
    return blanks
