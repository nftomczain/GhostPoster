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
