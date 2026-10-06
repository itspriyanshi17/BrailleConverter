from braille_converter import to_braille


def test_hello_and_number():
    assert to_braille("Hello 123").braille == "⠠⠓⠑⠇⠇⠕⠀⠼⠁⠃⠉"


def test_all_caps_word():
    assert to_braille("NASA").braille == "⠠⠠⠝⠁⠎⠁"


def test_letter_after_number_gets_grade1_sign():
    assert to_braille("4a").braille == "⠼⠙⠰⠁"


def test_decimal_stays_in_number():
    assert to_braille("3.14").braille == "⠼⠉⠲⠁⠙"


def test_punctuation():
    assert to_braille("hi, you!").braille == "⠓⠊⠂⠀⠽⠕⠥⠖"
