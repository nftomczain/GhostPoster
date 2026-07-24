"""Obliczanie siatki podziału dużej strony na mniejsze kafelki (arkusze).

Każdy kafelek ma rozmiar docelowego formatu papieru. Sąsiednie kafelki
nachodzą na siebie o `overlap_pt`, co daje wspólną zakładkę do sklejania
wydrukowanych arkuszy. Kafelki na prawym/dolnym brzegu strony są przycinane
do faktycznego rozmiaru źródłowej strony.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import ceil

from .utils import tile_label

# Tolerancja na szum zmiennoprzecinkowy: PyMuPDF zwraca rozmiar strony jako
# liczby pojedynczej precyzji, więc np. dokładnie 400mm może wrócić jako
# 400.00000000862mm. Bez tej poprawki taki mikroskopijny nadmiar potrafi
# przesunąć ceil() na drugą stronę granicy i dodać całkowicie zbędny,
# prawie pusty wiersz/kolumnę kafelków. 0.001 pt (~0.00035 mm) jest dużo
# mniejsze niż jakakolwiek fizycznie istotna różnica, a jednocześnie
# bezpiecznie większe od obserwowanego szumu.
_EPS_PT = 1e-3


@dataclass(frozen=True)
class Tile:
    """Pojedynczy kafelek: pozycja w siatce i prostokąt źródłowy (w punktach PDF)."""

    row: int
    col: int
    x0: float
    y0: float
    x1: float
    y1: float

    @property
    def width(self) -> float:
        return self.x1 - self.x0

    @property
    def height(self) -> float:
        return self.y1 - self.y0

    @property
    def label(self) -> str:
        return tile_label(self.row, self.col)


def compute_grid(
    page_width_pt: float,
    page_height_pt: float,
    paper_width_pt: float,
    paper_height_pt: float,
    overlap_pt: float,
) -> list[Tile]:
    """Wylicza listę kafelków pokrywających całą stronę źródłową.

    Args:
        page_width_pt: szerokość strony źródłowej PDF w punktach.
        page_height_pt: wysokość strony źródłowej PDF w punktach.
        paper_width_pt: szerokość docelowego arkusza (np. A3) w punktach.
        paper_height_pt: wysokość docelowego arkusza w punktach.
        overlap_pt: szerokość zakładki (nachodzenia kafelków) w punktach.

    Returns:
        Lista obiektów Tile w kolejności wiersz po wierszu, kolumna po kolumnie.
    """
    if paper_width_pt <= 0 or paper_height_pt <= 0:
        raise ValueError("Rozmiar arkusza docelowego musi być dodatni.")
    if overlap_pt < 0:
        raise ValueError("Zakładka (overlap) nie może być ujemna.")
    if overlap_pt >= paper_width_pt or overlap_pt >= paper_height_pt:
        raise ValueError("Zakładka jest większa niż rozmiar arkusza docelowego.")

    step_x = paper_width_pt - overlap_pt
    step_y = paper_height_pt - overlap_pt

    cols = max(1, ceil((page_width_pt - _EPS_PT) / step_x))
    rows = max(1, ceil((page_height_pt - _EPS_PT) / step_y))

    tiles: list[Tile] = []
    for row in range(rows):
        y0 = row * step_y
        y1 = min(y0 + paper_height_pt, page_height_pt)
        for col in range(cols):
            x0 = col * step_x
            x1 = min(x0 + paper_width_pt, page_width_pt)
            tiles.append(Tile(row=row, col=col, x0=x0, y0=y0, x1=x1, y1=y1))

    return tiles


@dataclass(frozen=True)
class GridResult:
    """Wynik doboru siatki: kafelki plus faktycznie użyty rozmiar/orientacja arkusza."""

    tiles: list[Tile]
    paper_width_pt: float
    paper_height_pt: float
    orientation: str  # "pionowo" albo "poziomo"


def compute_best_grid(
    page_width_pt: float,
    page_height_pt: float,
    paper_width_pt: float,
    paper_height_pt: float,
    overlap_pt: float,
) -> GridResult:
    """Wybiera orientację arkusza (pionowo/poziomo), która daje najmniej kartek.

    Skala zawsze pozostaje 100% (kafelki nigdy nie są przeskalowywane) —
    jedyne, co się zmienia, to czy arkusz jest ułożony pionowo czy poziomo,
    bo to wpływa na to, ile kafelków zmieści się w rzędzie/kolumnie.
    Przy remisie liczby kartek wygrywa orientacja zgodna z proporcjami
    strony źródłowej (żeby uniknąć nadmiaru pustego marginesu na kafelkach
    brzegowych).
    """
    candidates: list[GridResult] = []
    for width, height, orientation in (
        (paper_width_pt, paper_height_pt, "pionowo"),
        (paper_height_pt, paper_width_pt, "poziomo"),
    ):
        try:
            tiles = compute_grid(page_width_pt, page_height_pt, width, height, overlap_pt)
        except ValueError:
            continue
        candidates.append(
            GridResult(
                tiles=tiles, paper_width_pt=width, paper_height_pt=height, orientation=orientation
            )
        )

    if not candidates:
        raise ValueError("Żadna orientacja arkusza nie mieści zakładki — zmniejsz overlap.")

    page_is_landscape = page_width_pt >= page_height_pt

    def sort_key(result: GridResult) -> tuple[int, int]:
        result_is_landscape = result.paper_width_pt >= result.paper_height_pt
        orientation_mismatch = 0 if result_is_landscape == page_is_landscape else 1
        return (len(result.tiles), orientation_mismatch)

    candidates.sort(key=sort_key)
    return candidates[0]


def translate_tiles(tiles: list[Tile], dx: float, dy: float) -> list[Tile]:
    """Przesuwa listę kafelków o (dx, dy) — używane po Auto Crop, żeby
    kafelki policzone względem przyciętego obszaru wróciły do współrzędnych
    bezwzględnych oryginalnej strony źródłowej (tych, na których operuje
    `writer.write_tiled_pdf` przy wycinaniu fragmentów z PDF-a)."""
    return [
        Tile(row=t.row, col=t.col, x0=t.x0 + dx, y0=t.y0 + dy, x1=t.x1 + dx, y1=t.y1 + dy)
        for t in tiles
    ]
