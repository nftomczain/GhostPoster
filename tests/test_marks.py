"""Regresja: krzyże pasowania i linie cięcia muszą pojawić się na OBU
kafelkach dzielących wspólną granicę, nie tylko na jednym z nich.

Błąd znaleziony na realnym pliku użytkownika (siatka 1 wiersz x 2 kolumny,
A1 i B1): A1 (lewy kafelek) dostawał komplet znaczników, ale B1 (prawy,
bez własnego prawego/dolnego sąsiada) nie dostawał nic — mimo że dzieli
z A1 dokładnie tę samą granicę i fizycznie jest osobną kartką papieru,
której też potrzebne są znaczniki do wyrównania przy klejeniu.
"""

from __future__ import annotations

import fitz

from ghostposter.geometry import compute_grid
from ghostposter.marks import draw_cutlines, draw_registration_crosses


def _count_colored_drawings(page: fitz.Page) -> tuple[int, int]:
    """Zlicza elementy rysunkowe czerwone (cutline) i niebieskie (krzyże) na stronie."""
    red = blue = 0
    for item in page.get_drawings():
        color = item.get("color")
        if not color:
            continue
        r, g, b = color[:3]
        if r > 0.5 and g < 0.3 and b < 0.3:
            red += 1
        elif b > 0.5 and r < 0.3:
            blue += 1
    return red, blue


def test_two_tile_grid_both_sides_get_crosses_and_cutlines(tmp_path):
    """Siatka dokładnie 1x2 (jak w zgłoszonym błędzie): oba kafelki muszą
    mieć taką samą liczbę krzyży i taką samą liczbę linii cięcia."""
    tiles = compute_grid(
        page_width_pt=1000,
        page_height_pt=400,
        paper_width_pt=600,
        paper_height_pt=500,
        overlap_pt=50,
    )
    assert [t.label for t in tiles] == ["A1", "B1"]
    a1, b1 = tiles

    doc = fitz.open()
    page_a1 = doc.new_page(width=600, height=500)
    draw_registration_crosses(page_a1, a1, tiles)
    draw_cutlines(page_a1, a1, tiles)

    page_b1 = doc.new_page(width=600, height=500)
    draw_registration_crosses(page_b1, b1, tiles)
    draw_cutlines(page_b1, b1, tiles)

    out_path = tmp_path / "two_tile.pdf"
    doc.save(out_path)
    doc.close()

    reopened = fitz.open(out_path)
    red_a1, blue_a1 = _count_colored_drawings(reopened[0])
    red_b1, blue_b1 = _count_colored_drawings(reopened[1])

    assert red_a1 > 0, "A1 powinien mieć linię cięcia"
    assert blue_a1 > 0, "A1 powinien mieć krzyże pasowania"
    assert red_b1 == red_a1, "B1 musi mieć tyle samo linii cięcia co A1 (ta sama granica)"
    assert blue_b1 == blue_a1, "B1 musi mieć tyle samo krzyży co A1 (ta sama granica)"


def test_three_by_two_grid_every_shared_edge_symmetric(tmp_path):
    """Ogólniejsza wersja: dla większej siatki, każdy kafelek mający
    sąsiada z prawej musi mieć własną linię cięcia — i ten sąsiad też."""
    tiles = compute_grid(
        page_width_pt=1800,
        page_height_pt=900,
        paper_width_pt=600,
        paper_height_pt=500,
        overlap_pt=40,
    )
    by_rc = {(t.row, t.col): t for t in tiles}

    doc = fitz.open()
    order = list(tiles)
    for tile in order:
        page = doc.new_page(width=600, height=500)
        draw_registration_crosses(page, tile, tiles)
        draw_cutlines(page, tile, tiles)

    out_path = tmp_path / "grid.pdf"
    doc.save(out_path)
    doc.close()

    reopened = fitz.open(out_path)
    counts = {tile.label: _count_colored_drawings(reopened[i]) for i, tile in enumerate(order)}

    for (row, col), tile in by_rc.items():
        right = by_rc.get((row, col + 1))
        if right is not None:
            assert counts[tile.label][0] > 0, f"{tile.label} powinien mieć linię cięcia"
            assert counts[right.label][0] > 0, f"{right.label} powinien mieć linię cięcia"
