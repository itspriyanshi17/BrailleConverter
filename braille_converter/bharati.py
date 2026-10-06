"""Bharati Braille for Indian scripts (Hindi, Marathi, Nepali, Bengali, Gujarati,
Punjabi, Odia, Tamil, Telugu, Kannada, Malayalam).

Bharati Braille gives a sound the same cell in every Indian script: क, ক, க, క
and ಕ (all "ka") are all ⠅. Unicode puts these scripts in parallel 128-character
blocks with letters at the same offsets as Devanagari. So we define the table
once, keyed by offset inside the block, and add a few per-script overrides.

The cell assignments and rules follow liblouis's Indian tables
(devanagari.cti, bengali.cti, telugu.cti, ...):
  * Vowel signs (matras) use the same cell as the full vowel; the inherent "a"
    after a consonant is not written.
  * A dead consonant (consonant + halant) is written as ⠈ BEFORE the consonant:
    स्त -> ⠈⠎⠞.
  * A consonant followed directly by a full vowel letter gets an explicit ⠁, so
    it cannot be confused with consonant + matra.
  * क्ष -> ⠟ and ज्ञ -> ⠱ have their own cells.
"""

from .cells import UNKNOWN, dots

SCRIPT_BASES = {
    "devanagari": 0x0900,
    "bengali": 0x0980,
    "gurmukhi": 0x0A00,
    "gujarati": 0x0A80,
    "oriya": 0x0B00,
    "tamil": 0x0B80,
    "telugu": 0x0C00,
    "kannada": 0x0C80,
    "malayalam": 0x0D00,
}

# Offset inside the script block -> dot pattern.
TABLE = {
    # signs
    0x01: "3",       # chandrabindu
    0x02: "56",      # anusvara
    0x03: "6",       # visarga
    # independent vowels
    0x04: "1", 0x05: "1", 0x06: "345", 0x07: "24", 0x08: "35", 0x09: "136",
    0x0A: "1256", 0x0B: "5-1235", 0x0C: "5-123", 0x0D: "34", 0x0E: "26",
    0x0F: "15", 0x10: "34", 0x11: "1346", 0x12: "135", 0x13: "135", 0x14: "246",
    # consonants
    0x15: "13", 0x16: "46", 0x17: "1245", 0x18: "126", 0x19: "346",
    0x1A: "14", 0x1B: "16", 0x1C: "245", 0x1D: "356", 0x1E: "25",
    0x1F: "23456", 0x20: "2456", 0x21: "1246", 0x22: "123456", 0x23: "3456",
    0x24: "2345", 0x25: "1456", 0x26: "145", 0x27: "2346", 0x28: "1345",
    0x29: "56",
    0x2A: "1234", 0x2B: "235", 0x2C: "12", 0x2D: "45", 0x2E: "134",
    0x2F: "13456", 0x30: "1235", 0x31: "12456", 0x32: "123", 0x33: "456",
    0x34: "123", 0x35: "1236", 0x36: "146", 0x37: "12346", 0x38: "234",
    0x39: "125",
    0x3D: "2",       # avagraha
    # vowel signs (matras)
    0x3E: "345", 0x3F: "24", 0x40: "35", 0x41: "136", 0x42: "1256",
    0x43: "5-1235", 0x44: "6-1235", 0x45: "34", 0x46: "26", 0x47: "15",
    0x48: "34", 0x49: "1346", 0x4A: "135", 0x4B: "135", 0x4C: "246",
    0x50: "135-4-134",  # om
    0x57: "246",        # au length mark (Tamil, Malayalam, Odia)
    # nukta letters (written like the base letter, except ड़ and ढ़)
    0x58: "13", 0x59: "46", 0x5A: "1245", 0x5B: "245", 0x5C: "12456",
    0x5D: "5-12456", 0x5E: "235", 0x5F: "13456",
    0x60: "6-1235", 0x61: "6-123", 0x62: "5-123", 0x63: "6-123",
    0x64: "256", 0x65: "256-256",  # danda, double danda
    0x70: "256",                   # abbreviation sign
}

DIGIT_CELLS = ["245", "1", "12", "14", "145", "15", "124", "1245", "125", "24"]

# Characters whose cell differs from the Devanagari letter at the same offset.
OVERRIDES = {
    # Bengali / Assamese
    0x09CE: "4-2345",  # khanda ta
    0x09DF: "26",      # ya with nukta
    0x09F0: "1235",    # Assamese ra
    0x09F1: "1236",    # Assamese wa
    # Gurmukhi
    0x0A70: "56",      # tippi (nasal, like anusvara)
    # Gujarati
    0x0A8D: "26", 0x0AC5: "26",
    # Odia
    0x0B5F: "26", 0x0B56: "34",
    # Tamil
    0x0B8E: "26", 0x0BC6: "26",           # short e
    0x0B92: "1346", 0x0BCA: "1346",       # short o
    0x0BB4: "12356",                      # zha
    # Telugu, Kannada, Malayalam short o
    0x0C12: "1346", 0x0C4A: "1346",
    0x0C92: "1346", 0x0CCA: "1346",
    0x0D12: "1346", 0x0D4A: "1346",
    0x0D34: "12356",                      # Malayalam zha
    # Malayalam chillu letters (consonants with no vowel)
    0x0D7A: "4-3456", 0x0D7B: "4-1345", 0x0D7C: "4-1235",
    0x0D7D: "4-123", 0x0D7E: "4-456",
}

# Letter + nukta pairs with their own cell. NFC normalization splits य़-style
# precomposed letters into base + nukta, so these are matched on the pair.
NUKTA_FORMS = {
    0x0921: "12456", 0x0922: "5-12456",   # Devanagari ड़ ढ़
    0x09A1: "12456", 0x09A2: "5-12456",   # Bengali ড় ঢ়
    0x0B21: "12456", 0x0B22: "5-12456",   # Odia ଡ଼ ଢ଼
    0x09AF: "26", 0x0B2F: "26",           # Bengali য়, Odia ୟ
}

NUMBER = dots("3456")
HALANT_CELL = dots("4")
INHERENT_A = dots("1")
KSHA = dots("12345")
GYA = dots("156")

HALANT, NUKTA = 0x4D, 0x3C
ZERO_WIDTH = {"‌", "‍"}
DOTTED_CIRCLE = "◌"  # shown in front of a lone vowel sign in the visual view


def script_of(ch: str) -> str | None:
    cp = ord(ch)
    for name, base in SCRIPT_BASES.items():
        if base <= cp < base + 0x80:
            return name
    return None


def _offset(ch: str) -> int | None:
    script = script_of(ch)
    return None if script is None else ord(ch) - SCRIPT_BASES[script]


def _is_consonant(off: int | None) -> bool:
    return off is not None and (0x15 <= off <= 0x39 or 0x58 <= off <= 0x5F)


def _is_full_vowel(off: int | None) -> bool:
    return off is not None and (0x05 <= off <= 0x14 or off in (0x60, 0x61))


def _is_matra(off: int | None) -> bool:
    return off is not None and (0x3E <= off <= 0x4C or off in (0x62, 0x63)) and off != HALANT


def _cells_for(ch: str) -> str | None:
    cp = ord(ch)
    if cp in OVERRIDES:
        return dots(OVERRIDES[cp])
    off = _offset(ch)
    if off is None:
        return None
    if 0x66 <= off <= 0x6F:
        return dots(DIGIT_CELLS[off - 0x66])
    if off in TABLE:
        return dots(TABLE[off])
    return None


def translate(text: str) -> list[tuple[str, str]]:
    """Translate Indic-script text into (source, braille) pairs."""
    out: list[tuple[str, str]] = []
    chars = [c for c in text if c not in ZERO_WIDTH]
    offs = [_offset(c) for c in chars]
    in_number = False
    i = 0
    while i < len(chars):
        ch, off = chars[i], offs[i]
        nxt = lambda k: offs[i + k] if i + k < len(chars) else None  # noqa: E731

        if off is not None and 0x66 <= off <= 0x6F:
            out.append((ch, ("" if in_number else NUMBER) + _cells_for(ch)))
            in_number = True
            i += 1
            continue
        in_number = False

        if _is_consonant(off):
            # क्ष and ज्ञ have their own cells.
            if off == 0x15 and nxt(1) == HALANT and nxt(2) == 0x37:
                src, cells, used = "".join(chars[i:i + 3]), KSHA, 3
            elif off == 0x1C and nxt(1) == HALANT and nxt(2) == 0x1E:
                src, cells, used = "".join(chars[i:i + 3]), GYA, 3
            else:
                src, used = ch, 1
                if nxt(1) == NUKTA:
                    src += chars[i + 1]
                    used = 2
                    if ord(ch) in NUKTA_FORMS:
                        cells = dots(NUKTA_FORMS[ord(ch)])
                    else:
                        cells = _cells_for(ch)
                else:
                    cells = _cells_for(ch)
                cells = cells or UNKNOWN

            after = nxt(used)
            if after == HALANT:
                src += chars[i + used]
                cells = HALANT_CELL + cells
                used += 1
            elif _is_full_vowel(after):
                cells += INHERENT_A
            out.append((src, cells))
            i += used
            continue

        if off == NUKTA:  # stray nukta: nothing to write
            i += 1
            continue
        if off == HALANT:  # halant that is not after a consonant
            out.append((DOTTED_CIRCLE + ch, HALANT_CELL))
            i += 1
            continue

        cells = _cells_for(ch)
        label = DOTTED_CIRCLE + ch if _is_matra(off) or off in (0x01, 0x02, 0x03) else ch
        out.append((label, cells or UNKNOWN))
        i += 1
    return out
