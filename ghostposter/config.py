"""Konfiguracja pojedynczego zadania podziału PDF."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class TileJobConfig:
    """Parametry pojedynczego zadania GhostPoster."""

    input_path: Path
    output_path: Path
    paper: str = "A4"
    overlap_mm: float = 10.0
    page_number: int = 0  # strona źródłowego PDF, 0-based
    marks: bool = False  # v0.2
    cutlines: bool = False  # v0.2
    labels: bool = False  # v0.2
    maximize: bool = False  # auto-dobór orientacji arkusza, mniej kartek
    print_shop: bool = False  # tryb Drukarnia: stempel "nie skaluj" + karta zlecenia
    skip_blank: bool = False  # wymuś pomijanie pustych arkuszy bez pytania
    keep_blank: bool = False  # wymuś zachowanie wszystkich arkuszy bez pytania
    auto_crop: bool = False  # przytnij do rzeczywistego obszaru rysunku przed podziałem
    crop_margin_mm: float = 5.0  # margines wokół wykrytej treści przy auto_crop

    def __post_init__(self) -> None:
        if not (0 <= self.overlap_mm <= 50):
            raise ValueError("Zakładka (overlap) musi być w zakresie 0–50 mm.")
        if self.page_number < 0:
            raise ValueError("Numer strony nie może być ujemny.")
        if self.skip_blank and self.keep_blank:
            raise ValueError("--skip-blank i --keep-blank wykluczają się nawzajem.")
        if self.crop_margin_mm < 0:
            raise ValueError("Margines Auto Crop nie może być ujemny.")
