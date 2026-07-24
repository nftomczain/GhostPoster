import fitz
import pytest

from ghostposter.crop import detect_content_bbox
from ghostposter.geometry import compute_grid, translate_tiles


@pytest.fixture
def large_margins_pdf(tmp_path):
    """Strona 1200x800mm z tresc tylko w srodkowym bloku 500x300mm."""
    mm_to_pt = 72 / 25.4
    path = tmp_path / "margins.pdf"
    doc = fitz.open()
    page = doc.new_page(width=1200 * mm_to_pt, height=800 * mm_to_pt)
    block = fitz.Rect(
        350 * mm_to_pt, 250 * mm_to_pt, 850 * mm_to_pt, 550 * mm_to_pt
    )  # 500x300mm, wysrodkowany
    page.draw_rect(block, color=(0, 0, 0), width=2, fill=(0.9, 0.9, 0.9))
    doc.save(path)
    doc.close()
    return path


def test_detect_content_bbox_shrinks_to_drawn_block(large_margins_pdf):
    mm_to_pt = 72 / 25.4
    bbox = detect_content_bbox(large_margins_pdf, 0, padding_mm=5.0)

    # oczekujemy czegos w okolicy 500x300mm + 2*5mm paddingu, duzo mniej niz 1200x800mm
    assert bbox.width < 700 * mm_to_pt
    assert bbox.height < 500 * mm_to_pt
    assert bbox.width > 400 * mm_to_pt
    assert bbox.height > 200 * mm_to_pt


def test_auto_crop_reduces_tile_count(large_margins_pdf):
    mm_to_pt = 72 / 25.4
    paper_w, paper_h = 210 * mm_to_pt, 297 * mm_to_pt  # A4
    overlap_pt = 10 * mm_to_pt

    full_tiles = compute_grid(1200 * mm_to_pt, 800 * mm_to_pt, paper_w, paper_h, overlap_pt)

    bbox = detect_content_bbox(large_margins_pdf, 0, padding_mm=5.0)
    cropped_tiles = compute_grid(bbox.width, bbox.height, paper_w, paper_h, overlap_pt)

    assert len(cropped_tiles) < len(full_tiles)


def test_translate_tiles_shifts_coordinates_and_keeps_labels():
    tiles = compute_grid(1000, 1000, 500, 500, overlap_pt=0)
    shifted = translate_tiles(tiles, dx=100, dy=50)

    for original, moved in zip(tiles, shifted, strict=True):
        assert moved.label == original.label
        assert moved.x0 == original.x0 + 100
        assert moved.y0 == original.y0 + 50
        assert moved.x1 == original.x1 + 100
        assert moved.y1 == original.y1 + 50


def test_blank_page_returns_full_rect(tmp_path):
    path = tmp_path / "blank.pdf"
    doc = fitz.open()
    doc.new_page(width=500, height=500)
    doc.save(path)
    doc.close()

    bbox = detect_content_bbox(path, 0)
    assert bbox.width == pytest.approx(500, abs=1)
    assert bbox.height == pytest.approx(500, abs=1)
