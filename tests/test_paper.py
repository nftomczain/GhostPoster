import pytest

from ghostposter.paper import UnknownPaperSizeError, get_paper_size_mm, get_paper_size_pt


def test_a4_size_mm():
    width, height = get_paper_size_mm("A4")
    assert width == 210.0
    assert height == 297.0


def test_case_insensitive():
    assert get_paper_size_mm("a3") == get_paper_size_mm("A3")


def test_unknown_size_raises():
    with pytest.raises(UnknownPaperSizeError):
        get_paper_size_mm("A99")


def test_pt_conversion_matches_mm():
    width_pt, height_pt = get_paper_size_pt("A4")
    assert width_pt == pytest.approx(210.0 * 72 / 25.4)
    assert height_pt == pytest.approx(297.0 * 72 / 25.4)


def test_legal_size_mm():
    width, height = get_paper_size_mm("Legal")
    assert width == pytest.approx(215.9, abs=0.05)
    assert height == pytest.approx(355.6, abs=0.05)


def test_tabloid_size_mm():
    width, height = get_paper_size_mm("Tabloid")
    assert width == pytest.approx(279.4, abs=0.05)
    assert height == pytest.approx(431.8, abs=0.05)


def test_ansi_a_matches_letter():
    assert get_paper_size_mm("ANSI-A") == get_paper_size_mm("Letter")


def test_ansi_b_matches_tabloid():
    assert get_paper_size_mm("ANSI-B") == get_paper_size_mm("Tabloid")


@pytest.mark.parametrize("size", ["ANSI-C", "ANSI-D", "ANSI-E"])
def test_ansi_sizes_present_and_growing(size):
    width, height = get_paper_size_mm(size)
    assert width > 0 and height > 0


def test_ansi_series_increases_monotonically():
    sizes = [get_paper_size_mm(f"ANSI-{letter}") for letter in "ABCDE"]
    areas = [w * h for w, h in sizes]
    assert areas == sorted(areas)


@pytest.mark.parametrize("size", ["ARCH-A", "ARCH-B", "ARCH-C", "ARCH-D", "ARCH-E", "ARCH-E1"])
def test_arch_sizes_present(size):
    width, height = get_paper_size_mm(size)
    assert width > 0 and height > 0


def test_arch_a_size_mm():
    width, height = get_paper_size_mm("ARCH-A")
    assert width == pytest.approx(228.6, abs=0.05)
    assert height == pytest.approx(304.8, abs=0.05)


def test_lowercase_hyphenated_names_work():
    assert get_paper_size_mm("arch-d") == get_paper_size_mm("ARCH-D")


def test_a7_size_mm():
    width, height = get_paper_size_mm("A7")
    assert width == 74.0
    assert height == 105.0


def test_arch_order_is_a_b_c_d_e1_e():
    from ghostposter.paper import available_sizes

    sizes = available_sizes()
    arch = [s for s in sizes if s.startswith("ARCH")]
    assert arch == ["ARCH-A", "ARCH-B", "ARCH-C", "ARCH-D", "ARCH-E1", "ARCH-E"]
