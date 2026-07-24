"""Auto Crop / "Przytnij do treści": wykrywa faktyczny obszar rysunku na
stronie źródłowej (ignorując puste marginesy) i zwraca go jako prostokąt,
który można podać do `geometry.compute_grid` zamiast pełnego rozmiaru
strony. Dzięki temu strona z dużym pustym marginesem (np. wydruk z tytu-
łem w rogu i resztą białej kartki) dostaje od razu mniejszą, sensowną
siatkę arkuszy zamiast pełnej siatki z mnóstwem pustych kafelków do
odfiltrowania przez `blank.py`.

Metoda: renderujemy stronę w niskiej rozdzielczości w skali szarości,
progujemy do maski czarno-białej i bierzemy bounding box niepustych
pikseli (Pillow `Image.getbbox()` — szybkie, zaimplementowane w C).
"""

from __future__ import annotations

from pathlib import Path

import fitz
from PIL import Image

from .utils import mm_to_pt

_SAMPLE_MAX_PX = 1500
_WHITE_THRESHOLD = 250  # bajt >= tego uznajemy za "biały" (skala szarości 0-255)


def detect_content_bbox(
    input_path: Path,
    page_number: int,
    padding_mm: float = 5.0,
) -> fitz.Rect:
    """Zwraca prostokąt (we współrzędnych bezwzględnych strony, w punktach)
    obejmujący faktyczną treść strony, powiększony o `padding_mm` z każdej
    strony i przycięty do granic oryginalnej strony.

    Jeśli strona jest całkowicie pusta (nic do wykrycia), zwraca pełny
    prostokąt strony bez zmian — Auto Crop wtedy po prostu nic nie zmienia,
    zamiast zwracać zdegenerowany prostokąt o zerowym rozmiarze.
    """
    with fitz.open(input_path) as doc:
        page = doc[page_number]
        rect = page.rect
        scale = min(_SAMPLE_MAX_PX / max(rect.width, rect.height, 1e-6), 3.0)
        scale = max(scale, 0.02)

        pix = page.get_pixmap(matrix=fitz.Matrix(scale, scale), colorspace=fitz.csGRAY)
        img = Image.frombytes("L", (pix.width, pix.height), pix.samples)
        mask = img.point(lambda p: 255 if p < _WHITE_THRESHOLD else 0)
        bbox_px = mask.getbbox()

        if bbox_px is None:
            return fitz.Rect(rect)

        x0_px, y0_px, x1_px, y1_px = bbox_px
        pad = mm_to_pt(padding_mm)
        content = fitz.Rect(
            x0_px / scale - pad,
            y0_px / scale - pad,
            x1_px / scale + pad,
            y1_px / scale + pad,
        )

        # przycinamy do granic prawdziwej strony — padding nie moze
        # "wypchnac" prostokata poza faktyczny obszar strony
        content.x0 = max(content.x0, rect.x0)
        content.y0 = max(content.y0, rect.y0)
        content.x1 = min(content.x1, rect.x1)
        content.y1 = min(content.y1, rect.y1)
        return content
