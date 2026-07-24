import pytest

from ghostposter.geometry import compute_grid


def test_single_tile_when_page_fits_on_one_sheet():
    tiles = compute_grid(
        page_width_pt=500,
        page_height_pt=700,
        paper_width_pt=600,
        paper_height_pt=800,
        overlap_pt=0,
    )
    assert len(tiles) == 1
    tile = tiles[0]
    assert (tile.x0, tile.y0, tile.x1, tile.y1) == (0, 0, 500, 700)
    assert tile.label == "A1"


def test_grid_splits_into_expected_number_of_tiles_without_overlap():
    # Strona dokładnie 2x szersza i 2x wyższa niż arkusz -> siatka 2x2
    tiles = compute_grid(
        page_width_pt=1000,
        page_height_pt=1000,
        paper_width_pt=500,
        paper_height_pt=500,
        overlap_pt=0,
    )
    assert len(tiles) == 4
    labels = {tile.label for tile in tiles}
    assert labels == {"A1", "B1", "A2", "B2"}


def test_overlap_creates_shared_band_between_tiles():
    tiles = compute_grid(
        page_width_pt=900,
        page_height_pt=500,
        paper_width_pt=500,
        paper_height_pt=500,
        overlap_pt=100,
    )
    # step_x = 500 - 100 = 400; ceil(900 / 400) = 3 kolumny (0, 400, 800)
    cols = sorted({tile.col for tile in tiles})
    assert cols == [0, 1, 2]
    first_col_tile = next(t for t in tiles if t.col == 0)
    second_col_tile = next(t for t in tiles if t.col == 1)
    # nachodzenie: drugi kafelek zaczyna sie przed koncem pierwszego
    assert second_col_tile.x0 < first_col_tile.x1


def test_negative_overlap_raises():
    with pytest.raises(ValueError):
        compute_grid(100, 100, 50, 50, overlap_pt=-1)


def test_overlap_larger_than_paper_raises():
    with pytest.raises(ValueError):
        compute_grid(100, 100, 50, 50, overlap_pt=60)


def test_best_grid_picks_landscape_for_wide_page():
    from ghostposter.geometry import compute_best_grid

    # strona szeroka (1600x500), arkusz podany jako 500x800 (pionowo)
    # poziomo (800x500) powinien dac mniej kolumn przy tej samej wysokosci
    result = compute_best_grid(
        page_width_pt=1600,
        page_height_pt=500,
        paper_width_pt=500,
        paper_height_pt=800,
        overlap_pt=0,
    )
    assert result.orientation == "poziomo"
    assert result.paper_width_pt == 800
    assert result.paper_height_pt == 500


def test_best_grid_matches_manual_grid_tile_count():
    from ghostposter.geometry import compute_best_grid

    result = compute_best_grid(1000, 1000, 500, 500, overlap_pt=0)
    # kwadratowa strona i kwadratowy arkusz -> obie orientacje rownowazne
    assert len(result.tiles) == 4


def test_grid_tolerates_floating_point_noise_at_exact_boundary():
    """Regresja: PyMuPDF zwraca rozmiar strony jako float pojedynczej precyzji.

    Odkryte przy generowaniu przykładu plan_multipage.pdf (strona 1500x400mm,
    format A4 poziomo, overlap 10mm): matematycznie strona mieści się w
    dokładnie 2 rzędach kafelków, ale odczytany z PDF page.rect.height
    (1133.8582763671875 pt) jest o ok. 1e-5 pt większy niż dokładna wartość
    z przeliczenia mm->pt (1133.8582677165354 pt). Bez epsilon w compute_grid
    to niezauważalne dla oka przekroczenie granicy dawało ceil() = 3 zamiast
    2 — czyli zbędny, prawie pusty trzeci rząd arkuszy.
    """
    paper_width_pt = 297 * 72 / 25.4  # A4 poziomo: szersza strona
    paper_height_pt = 210 * 72 / 25.4
    overlap_pt = 10 * 72 / 25.4
    step_y = paper_height_pt - overlap_pt  # dokladnie tyle miejsca na "2 rzedy"

    # symulujemy szum PyMuPDF: strona odrobine wieksza niz dokladne 2*step_y
    noisy_page_height_pt = 2 * step_y + 1e-5

    tiles = compute_grid(500, noisy_page_height_pt, paper_width_pt, paper_height_pt, overlap_pt)
    rows = max(t.row for t in tiles) + 1
    assert rows == 2, "szum zmiennoprzecinkowy nie powinien dodawac zbednego rzedu kafelkow"
