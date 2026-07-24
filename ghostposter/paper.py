"""Standardowe formaty papieru (szerokość x wysokość w mm, orientacja pionowa)."""

from __future__ import annotations

from .utils import mm_to_pt

# Szerokość, wysokość w mm (portrait / pionowo)
PAPER_SIZES_MM: dict[str, tuple[float, float]] = {
    "A0": (841.0, 1189.0),
    "A1": (594.0, 841.0),
    "A2": (420.0, 594.0),
    "A3": (297.0, 420.0),
    "A4": (210.0, 297.0),
    "A5": (148.0, 210.0),
    "A6": (105.0, 148.0),
    "LETTER": (215.9, 279.4),
}


class UnknownPaperSizeError(ValueError):
    """Podano nieznany format papieru."""


def available_sizes() -> list[str]:
    """Zwraca listę obsługiwanych nazw formatów papieru."""
    return list(PAPER_SIZES_MM.keys())


def get_paper_size_mm(name: str) -> tuple[float, float]:
    """Zwraca (szerokość_mm, wysokość_mm) dla nazwy formatu, np. 'A3'."""
    key = name.strip().upper()
    if key not in PAPER_SIZES_MM:
        raise UnknownPaperSizeError(
            f"Nieznany format papieru: '{name}'. Dostępne: {', '.join(available_sizes())}"
        )
    return PAPER_SIZES_MM[key]


def get_paper_size_pt(name: str) -> tuple[float, float]:
    """Zwraca (szerokość_pt, wysokość_pt) dla nazwy formatu."""
    width_mm, height_mm = get_paper_size_mm(name)
    return mm_to_pt(width_mm), mm_to_pt(height_mm)
