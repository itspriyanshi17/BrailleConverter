import pytest

from braille_converter import to_braille


@pytest.mark.parametrize("text, expected", [
    ("नमस्ते", "⠝⠍⠈⠎⠞⠑"),        # halant written before the consonant
    ("भारत", "⠘⠜⠗⠞"),
    ("क्षमा", "⠟⠍⠜"),            # क्ष has its own cell
    ("ज्ञान", "⠱⠜⠝"),            # ज्ञ has its own cell
    ("कई", "⠅⠁⠔"),               # explicit 'a' before a full vowel
    ("पढ़ाई", "⠏⠐⠻⠜⠔"),           # ढ़ (nukta)
    ("हिंदी", "⠓⠊⠰⠙⠔"),           # anusvara
    ("१२३", "⠼⠁⠃⠉"),             # Devanagari digits
    ("राम।", "⠗⠜⠍⠲"),            # danda
])
def test_hindi(text, expected):
    assert to_braille(text).braille == expected


def test_same_sound_same_cell_across_scripts():
    # ka in Devanagari, Bengali, Gurmukhi, Gujarati, Odia, Tamil, Telugu, Kannada, Malayalam
    for ka in "कকਕકକகకಕക":
        assert to_braille(ka).braille == "⠅", ka


def test_other_scripts():
    assert to_braille("বাংলা").braille == "⠃⠜⠰⠇⠜"
    assert to_braille("தமிழ்").braille == "⠞⠍⠊⠈⠷"
    assert to_braille("తెలుగు").braille == "⠞⠢⠇⠥⠛⠥"


def test_bengali_ya_nukta_survives_normalization():
    assert to_braille("য়").braille == "⠢"


def test_mixed_english_and_hindi():
    r = to_braille("Hi नमस्ते")
    assert r.braille == "⠠⠓⠊⠀⠝⠍⠈⠎⠞⠑"
    assert not r.unknown


def test_unknown_characters_are_reported():
    r = to_braille("a€")
    assert r.braille.endswith("⠿")
    assert r.unknown == ["€"]


def test_ocr_danda_misread_is_fixed():
    from braille_converter.ocr import DANDA_MISREAD

    assert DANDA_MISREAD.sub("।", "देश हैl\nपसंद है|") == "देश है।\nपसंद है।"
    assert DANDA_MISREAD.sub("।", "Hello l world") == "Hello l world"
