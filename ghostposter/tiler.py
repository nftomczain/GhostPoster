"""Wczytuje źródłowy PDF i wylicza siatkę kafelków dla wybranej strony."""

from __future__ import annotations

from pathlib import Path

import fitz  # PyMuPDF

from .geometry import Tile, compute_grid
from .utils import mm_to_pt


class PageNumberOutOfRangeError(ValueError):
    """Żądana strona nie istnieje w dokumencie źródłowym."""


def get_page_size_pt(input_path: Path, page_number: int = 0) -> tuple[float, float]:
    """Zwraca (szerokość_pt, wysokość_pt) wybranej strony źródłowego PDF."""
    with fitz.open(input_path) as doc:
        if page_number >= len(doc):
            raise PageNumberOutOfRangeError(
                f"Dokument ma {len(doc)} stron(y), a żądano strony {page_number}."
            )
        page = doc[page_number]
        rect = page.rect
        return rect.width, rect.height


def plan_tiles(
    input_path: Path,
    paper_width_pt: float,
    paper_height_pt: float,
    overlap_mm: float,
    page_number: int = 0,
) -> list[Tile]:
    """Wylicza listę kafelków pokrywających wybraną stronę źródłowego PDF."""
    page_width_pt, page_height_pt = get_page_size_pt(input_path, page_number)
    overlap_pt = mm_to_pt(overlap_mm)
    return compute_grid(
        page_width_pt=page_width_pt,
        page_height_pt=page_height_pt,
        paper_width_pt=paper_width_pt,
        paper_height_pt=paper_height_pt,
        overlap_pt=overlap_pt,
    )
