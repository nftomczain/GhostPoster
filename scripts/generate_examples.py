"""Generuje syntetyczne pliki PDF do testowania GhostPoster na różnych
przypadkach: bardzo duży plan (A0), plan z dużymi pustymi marginesami,
plik wielostronicowy i wąski/wysoki plan.

Uruchomienie: `python scripts/generate_examples.py`
Pliki trafiają do `examples/`. Każdy ma naniesioną siatkę co 100 mm i
przekątną, żeby po sklejeniu wydrukowanych arkuszy łatwo zobaczyć
gołym okiem, czy podział/zakładki się zgadzają.
"""

from __future__ import annotations

from pathlib import Path

import fitz

MM_TO_PT = 72 / 25.4
EXAMPLES_DIR = Path(__file__).resolve().parent.parent / "examples"


def mm(value: float) -> float:
    return value * MM_TO_PT


def _draw_reference_grid(page: fitz.Page, width_mm: float, height_mm: float) -> None:
    """Siatka co 100mm (cienka, szara) + przekątna — do wizualnej kontroli sklejenia."""
    w, h = mm(width_mm), mm(height_mm)
    page.draw_rect(fitz.Rect(0, 0, w, h), color=(0, 0, 0), width=1.5)
    for x in range(100, int(width_mm), 100):
        page.draw_line((mm(x), 0), (mm(x), h), color=(0.7, 0.7, 0.7), width=0.4)
    for y in range(100, int(height_mm), 100):
        page.draw_line((0, mm(y)), (w, mm(y)), color=(0.7, 0.7, 0.7), width=0.4)
    page.draw_line((0, 0), (w, h), color=(0.9, 0.3, 0.3), width=1.0)
    page.draw_line((0, h), (w, 0), color=(0.9, 0.3, 0.3), width=1.0)


def make_a0_poster() -> None:
    """Pojedyncza strona dokładnie w formacie A0 (841x1189mm) — duży plakat."""
    doc = fitz.open()
    page = doc.new_page(width=mm(841), height=mm(1189))
    _draw_reference_grid(page, 841, 1189)
    page.insert_text((mm(15), mm(30)), "PLAN A0 (841 x 1189 mm)", fontsize=28, fontname="hebo")
    page.insert_text(
        (mm(15), mm(45)),
        "Siatka co 100mm, przekatne rog-rog do kontroli sklejenia arkuszy.",
        fontsize=11,
    )
    doc.save(EXAMPLES_DIR / "plan_A0_poster.pdf")
    doc.close()


def make_large_margins() -> None:
    """Duża strona (1200x800mm), ale treść tylko w środkowym bloku 500x300mm.

    Test przypadku, gdy większość kafelków brzegowych jest praktycznie pusta —
    sprawdza, czy podział i znaczniki nadal mają sens, gdy nie ma tam nic
    ciekawego do wydruku.
    """
    doc = fitz.open()
    w_mm, h_mm = 1200, 800
    page = doc.new_page(width=mm(w_mm), height=mm(h_mm))

    block_w, block_h = 500, 300
    x0 = (w_mm - block_w) / 2
    y0 = (h_mm - block_h) / 2
    block_rect = fitz.Rect(mm(x0), mm(y0), mm(x0 + block_w), mm(y0 + block_h))
    page.draw_rect(block_rect, color=(0, 0, 0), width=2, fill=(0.95, 0.95, 1.0))
    page.insert_text(
        (mm(x0 + 10), mm(y0 + 20)),
        "JEDYNA TRESC — reszta strony to pusty margines",
        fontsize=13,
        fontname="hebo",
    )
    page.insert_text(
        (mm(15), mm(20)),
        f"PLAN Z DUZYM MARGINESEM ({w_mm} x {h_mm} mm, tresc: {block_w}x{block_h} mm)",
        fontsize=16,
        fontname="hebo",
    )
    doc.save(EXAMPLES_DIR / "plan_large_margins.pdf")
    doc.close()


def make_multipage() -> None:
    """PDF z 3 stronami o różnych rozmiarach — test flagi `--page`."""
    doc = fitz.open()
    pages_mm = [(400, 300), (900, 500), (1500, 400)]
    for i, (w_mm, h_mm) in enumerate(pages_mm):
        page = doc.new_page(width=mm(w_mm), height=mm(h_mm))
        _draw_reference_grid(page, w_mm, h_mm)
        page.insert_text(
            (mm(15), mm(30)),
            f"STRONA {i} — {w_mm} x {h_mm} mm",
            fontsize=20,
            fontname="hebo",
        )
    doc.save(EXAMPLES_DIR / "plan_multipage.pdf")
    doc.close()


def make_wide_strip() -> None:
    """Bardzo szeroki, niski plan (np. elewacja / skrzydło) — dobry przypadek dla --maximize."""
    doc = fitz.open()
    w_mm, h_mm = 2000, 350
    page = doc.new_page(width=mm(w_mm), height=mm(h_mm))
    _draw_reference_grid(page, w_mm, h_mm)
    page.insert_text(
        (mm(15), mm(30)),
        f"PASEK/ELEWACJA ({w_mm} x {h_mm} mm) — przyklad dla --maximize",
        fontsize=18,
        fontname="hebo",
    )
    doc.save(EXAMPLES_DIR / "plan_wide_strip.pdf")
    doc.close()


def main() -> None:
    EXAMPLES_DIR.mkdir(exist_ok=True)
    make_a0_poster()
    make_large_margins()
    make_multipage()
    make_wide_strip()
    print(f"Zapisano przykłady do {EXAMPLES_DIR}")


if __name__ == "__main__":
    main()
