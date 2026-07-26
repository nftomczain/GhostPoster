"""Standardowe formaty papieru (szerokość x wysokość w mm, orientacja pionowa)."""

from __future__ import annotations

from .utils import mm_to_pt

_IN_TO_MM = 25.4

# Szerokość, wysokość w mm (portrait / pionowo)
PAPER_SIZES_MM: dict[str, tuple[float, float]] = {
    # ISO 216
    "A0": (841.0, 1189.0),
    "A1": (594.0, 841.0),
    "A2": (420.0, 594.0),
    "A3": (297.0, 420.0),
    "A4": (210.0, 297.0),
    "A5": (148.0, 210.0),
    "A6": (105.0, 148.0),
    "A7": (74.0, 105.0),
    # US - biurowe
    "LETTER": (8.5 * _IN_TO_MM, 11 * _IN_TO_MM),
    "LEGAL": (8.5 * _IN_TO_MM, 14 * _IN_TO_MM),
    "TABLOID": (11 * _IN_TO_MM, 17 * _IN_TO_MM),
    # ANSI (US, techniczne/inżynierskie) - A == Letter, B == Tabloid
    "ANSI-A": (8.5 * _IN_TO_MM, 11 * _IN_TO_MM),
    "ANSI-B": (11 * _IN_TO_MM, 17 * _IN_TO_MM),
    "ANSI-C": (17 * _IN_TO_MM, 22 * _IN_TO_MM),
    "ANSI-D": (22 * _IN_TO_MM, 34 * _IN_TO_MM),
    "ANSI-E": (34 * _IN_TO_MM, 44 * _IN_TO_MM),
    # ARCH (US, architektoniczne)
    "ARCH-A": (9 * _IN_TO_MM, 12 * _IN_TO_MM),
    "ARCH-B": (12 * _IN_TO_MM, 18 * _IN_TO_MM),
    "ARCH-C": (18 * _IN_TO_MM, 24 * _IN_TO_MM),
    "ARCH-D": (24 * _IN_TO_MM, 36 * _IN_TO_MM),
    "ARCH-E1": (30 * _IN_TO_MM, 42 * _IN_TO_MM),
    "ARCH-E": (36 * _IN_TO_MM, 48 * _IN_TO_MM),
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
