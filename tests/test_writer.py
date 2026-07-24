import fitz
import pytest

from ghostposter.geometry import compute_grid
from ghostposter.writer import write_tiled_pdf


@pytest.fixture
def source_pdf(tmp_path):
    mm_to_pt = 72 / 25.4
    path = tmp_path / "source.pdf"
    doc = fitz.open()
    doc.new_page(width=900 * mm_to_pt, height=600 * mm_to_pt)
    doc.save(path)
    doc.close()
    return path


def test_write_tiled_pdf_basic(source_pdf, tmp_path):
    tiles = compute_grid(
        900 * 72 / 25.4, 600 * 72 / 25.4, 297 * 72 / 25.4, 420 * 72 / 25.4, overlap_pt=10
    )
    out_path = tmp_path / "out.pdf"
    write_tiled_pdf(
        input_path=source_pdf,
        output_path=out_path,
        tiles=tiles,
        paper_width_pt=297 * 72 / 25.4,
        paper_height_pt=420 * 72 / 25.4,
    )
    doc = fitz.open(out_path)
    assert len(doc) == len(tiles)


def test_print_shop_mode_adds_info_page_and_stamps(source_pdf, tmp_path):
    paper_w, paper_h = 297 * 72 / 25.4, 420 * 72 / 25.4
    tiles = compute_grid(900 * 72 / 25.4, 600 * 72 / 25.4, paper_w, paper_h, overlap_pt=10)
    out_path = tmp_path / "out_print_shop.pdf"

    write_tiled_pdf(
        input_path=source_pdf,
        output_path=out_path,
        tiles=tiles,
        paper_width_pt=paper_w,
        paper_height_pt=paper_h,
        print_shop=True,
        print_shop_info={"Plik źródłowy": "source.pdf", "Format arkusza": "A3"},
    )

    doc = fitz.open(out_path)
    # +1 strona informacyjna na poczatku
    assert len(doc) == len(tiles) + 1

    info_text = doc[0].get_text()
    assert "KARTA ZLECENIA DRUKU" in info_text
    assert "A3" in info_text
    # regresja: polskie znaki diakrytyczne musza renderowac sie poprawnie,
    # a nie jako "·" (blad bazowej czcionki PyMuPDF, patrz marks.py)
    assert "Wydrukować" in info_text
    assert "źródłowy" in info_text
    assert "·" not in info_text

    tile_text = doc[1].get_text()
    assert "SKALOWA" in tile_text


def test_progress_callback_reports_every_tile(source_pdf, tmp_path):
    paper_w, paper_h = 297 * 72 / 25.4, 420 * 72 / 25.4
    tiles = compute_grid(900 * 72 / 25.4, 600 * 72 / 25.4, paper_w, paper_h, overlap_pt=10)
    out_path = tmp_path / "out_progress.pdf"

    seen = []
    write_tiled_pdf(
        input_path=source_pdf,
        output_path=out_path,
        tiles=tiles,
        paper_width_pt=paper_w,
        paper_height_pt=paper_h,
        progress_callback=lambda done, total: seen.append((done, total)),
    )
    assert seen == [(i, len(tiles)) for i in range(1, len(tiles) + 1)]
