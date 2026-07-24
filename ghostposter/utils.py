"""Drobne funkcje pomocnicze używane w całym projekcie."""

from __future__ import annotations

# 1 mm = 72 / 25.4 pt (punkt PDF/PostScript)
MM_TO_PT = 72.0 / 25.4


def mm_to_pt(value_mm: float) -> float:
    """Konwertuje milimetry na punkty PDF."""
    return value_mm * MM_TO_PT


def pt_to_mm(value_pt: float) -> float:
    """Konwertuje punkty PDF na milimetry."""
    return value_pt / MM_TO_PT


def column_letter(index: int) -> str:
    """Zamienia indeks kolumny (0-based) na literę: 0->A, 1->B, ..., 25->Z, 26->AA."""
    letters = ""
    index += 1
    while index > 0:
        index, remainder = divmod(index - 1, 26)
        letters = chr(65 + remainder) + letters
    return letters


def tile_label(row: int, col: int) -> str:
    """Etykieta kafelka w stylu arkuszowym, np. wiersz 0/kolumna 0 -> 'A1'."""
    return f"{column_letter(col)}{row + 1}"
