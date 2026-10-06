"""Helpers for building Unicode Braille cells from dot numbers.

A Braille cell has six dots numbered like this:

    1 4
    2 5
    3 6

Unicode Braille Patterns start at U+2800; each dot adds one bit:
dot 1 = 0x01, dot 2 = 0x02, dot 3 = 0x04, dot 4 = 0x08, dot 5 = 0x10, dot 6 = 0x20.
"""

BLANK = "⠀"
UNKNOWN = "⠿"  # all six dots, used for characters we cannot translate


def cell(dot_numbers: str) -> str:
    """'134' -> '⠍'.  '0' or '' -> blank cell."""
    mask = 0
    for d in dot_numbers:
        if d != "0":
            mask |= 1 << (int(d) - 1)
    return chr(0x2800 + mask)


def dots(spec: str) -> str:
    """'4-13' -> '⠈⠅'.  Several cells are separated by '-'."""
    return "".join(cell(part) for part in spec.split("-"))


def raised_dots(braille_char: str) -> list[int]:
    """'⠍' -> [1, 3, 4]."""
    mask = ord(braille_char) - 0x2800
    return [d for d in range(1, 7) if mask & (1 << (d - 1))]
