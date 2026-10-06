from braille_converter import to_braille
from braille_converter.export import from_brf, to_brf
from braille_converter.render import terminal_cells


def test_brf_ascii_mapping():
    assert to_brf(to_braille("hello world").braille) == "HELLO WORLD\r\n"


def test_brf_round_trip():
    braille = to_braille("नमस्ते Hello 42").braille
    assert from_brf(to_brf(braille)) == braille + "\n"


def test_brf_wraps_at_40_cells():
    brf = to_brf(to_braille("word " * 30).braille)
    assert all(len(line) <= 40 for line in brf.split("\r\n"))


def test_terminal_cells_shows_dots_and_letter():
    out = terminal_cells(to_braille("a").units).splitlines()
    assert out == ["●○", "○○", "○○", "a"]
