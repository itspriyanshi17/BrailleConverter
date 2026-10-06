"""English (and other Latin-script text) to Unified English Braille, Grade 1.

Grade 1 means letter-by-letter, without contractions, which is what most
learners start with and what maps cleanly back to the printed letters.
"""

from .cells import BLANK, UNKNOWN, dots

LETTERS = {
    "a": "1", "b": "12", "c": "14", "d": "145", "e": "15", "f": "124",
    "g": "1245", "h": "125", "i": "24", "j": "245", "k": "13", "l": "123",
    "m": "134", "n": "1345", "o": "135", "p": "1234", "q": "12345",
    "r": "1235", "s": "234", "t": "2345", "u": "136", "v": "1236",
    "w": "2456", "x": "1346", "y": "13456", "z": "1356",
}

# Digits 1-9, 0 reuse the letters a-j after a number sign.
DIGITS = {d: LETTERS[l] for d, l in zip("1234567890", "abcdefghij")}

PUNCTUATION = {
    ",": "2", ";": "23", ":": "25", ".": "256", "!": "235", "?": "236",
    "'": "3", "’": "3", "‘": "6-236", '"': "6-356",
    "“": "236", "”": "356", "-": "36", "–": "6-36",
    "—": "6-36", "(": "5-126", ")": "5-345", "[": "46-126",
    "]": "46-345", "/": "456-34", "&": "4-12346", "@": "4-1",
    "%": "46-356", "+": "5-235", "=": "5-2356", "*": "5-35",
    "#": "456-1456", "$": "4-234", "₹": "4-1235",
    "।": "256", "॥": "256-256",  # danda (often appears between Indic words)
}

CAPITAL = dots("6")
CAPS_WORD = dots("6-6")
NUMBER = dots("3456")
GRADE1 = dots("56")  # tells the reader "letter, not digit" right after a number


def translate(text: str) -> list[tuple[str, str]]:
    """Translate text into (source, braille) pairs, one pair per printed character."""
    out: list[tuple[str, str]] = []
    in_number = False
    i = 0
    while i < len(text):
        ch = text[i]

        if ch.isascii() and ch.isdigit():
            prefix = "" if in_number else NUMBER
            out.append((ch, prefix + dots(DIGITS[ch])))
            in_number = True
            i += 1
            continue

        # A '.' or ',' between two digits stays inside the number (3.14, 1,000).
        if in_number and ch in ".," and i + 1 < len(text) and text[i + 1].isdigit():
            out.append((ch, dots(PUNCTUATION[ch])))
            i += 1
            continue

        lower = ch.lower()
        if lower in LETTERS:
            prefix = GRADE1 if in_number and lower in "abcdefghij" else ""
            in_number = False
            if ch.isupper():
                # Whole word in capitals (2+ letters): one caps-word sign up front.
                j = i
                while j < len(text) and text[j].isascii() and text[j].isalpha():
                    j += 1
                word = text[i:j]
                if len(word) >= 2 and word.isupper():
                    for k, c in enumerate(word):
                        cap = CAPS_WORD if k == 0 else ""
                        out.append((c, (prefix if k == 0 else "") + cap + dots(LETTERS[c.lower()])))
                    i = j
                    continue
                prefix += CAPITAL
            out.append((ch, prefix + dots(LETTERS[lower])))
            i += 1
            continue

        in_number = False
        if ch == " " or ch == "\t":
            out.append((ch, BLANK))
        elif ch == "\n":
            out.append((ch, "\n"))
        elif ch in PUNCTUATION:
            out.append((ch, dots(PUNCTUATION[ch])))
        else:
            out.append((ch, UNKNOWN))
        i += 1
    return out
