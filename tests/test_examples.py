"""Testy 'smoke' na syntetycznych plikach z examples/ — każdy przypadek
ma sprawdzić, że pełny łańcuch (odczyt strony -> siatka -> zapis PDF)
działa bez wyjątków i daje sensowną liczbę arkuszy. To właśnie na jednym
z tych plików (plan_multipage.pdf, strona 1500x400mm) wykryty został
błąd precyzji zmiennoprzecinkowej opisany w test_geometry.py.
"""

from pathlib import Path

import fitz
import pytest

from ghostposter.geometry import compute_best_grid, compute_grid
from ghostposter.paper import get_paper_size_pt
from ghostposter.tiler import PageNumberOutOfRangeError, get_page_size_pt
from ghostposter.utils import mm_to_pt
from ghostposter.writer import write_tiled_pdf

EXAMPLES_DIR = Path(__file__).resolve().parent.parent / "examples"


@pytest.fixture(scope="module", autouse=True)
def ensure_examples_exist():
    """Generuje przykłady, jeśli ktoś uruchamia testy na świeżym klonie repo
    bez wcześniejszego `python scripts/generate_examples.py`."""
    needed = [
        "plan_A0_poster.pdf",
        "plan_large_margins.pdf",
        "plan_multipage.pdf",
        "plan_wide_strip.pdf",
    ]
    if not all((EXAMPLES_DIR / name).exists() for name in needed):
        import scripts.generate_examples as gen

        gen.main()


@pytest.mark.parametrize(
    "filename,page_number",
    [
        ("plan_A0_poster.pdf", 0),
        ("plan_large_margins.pdf", 0),
        ("plan_wide_strip.pdf", 0),
        ("plan_multipage.pdf", 0),
        ("plan_multipage.pdf", 1),
        ("plan_multipage.pdf", 2),
    ],
)
def test_example_tiles_without_error(filename, page_number, tmp_path):
    path = EXAMPLES_DIR / filename
    paper_w, paper_h = get_paper_size_pt("A3")
    page_w, page_h = get_page_size_pt(path, page_number)
    tiles = compute_grid(page_w, page_h, paper_w, paper_h, overlap_pt=mm_to_pt(10))

    assert len(tiles) >= 1

    out_path = tmp_path / f"{filename}_{page_number}_out.pdf"
    write_tiled_pdf(
        input_path=path,
        output_path=out_path,
        tiles=tiles,
        paper_width_pt=paper_w,
        paper_height_pt=paper_h,
        page_number=page_number,
        draw_marks=True,
        draw_cutlines=True,
        draw_labels=True,
    )
    doc = fitz.open(out_path)
    assert len(doc) == len(tiles)


def test_multipage_invalid_page_raises_clear_error():
    path = EXAMPLES_DIR / "plan_multipage.pdf"
    with pytest.raises(PageNumberOutOfRangeError):
        get_page_size_pt(path, 99)


@pytest.mark.parametrize(
    "filename,page_number",
    [
        ("plan_wide_strip.pdf", 0),  # bardzo szeroki, niski plan
        ("plan_multipage.pdf", 2),  # 1500x400mm — przypadek z odkrytym bugiem
    ],
)
def test_maximize_never_produces_more_tiles_than_default_orientation(filename, page_number):
    """--maximize ma z definicji dawać liczbę arkuszy <= domyślnej orientacji."""
    path = EXAMPLES_DIR / filename
    paper_w, paper_h = get_paper_size_pt("A4")
    page_w, page_h = get_page_size_pt(path, page_number)
    overlap_pt = mm_to_pt(10)

    default_tiles = compute_grid(page_w, page_h, paper_w, paper_h, overlap_pt)
    best = compute_best_grid(page_w, page_h, paper_w, paper_h, overlap_pt)

    assert len(best.tiles) <= len(default_tiles)
