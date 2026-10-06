"""Save Braille as files: Unicode text (.txt) and embosser-ready ASCII Braille (.brf)."""

from .cells import BLANK

# North American ASCII Braille: character for each dot pattern 0-63 (dots 1-6 as bits).
ASCII_BRAILLE = " A1B'K2L@CIF/MSP\"E3H9O6R^DJG>NTQ,*5<-U8V.%[$+X!&;:4\\0Z7(_?W]#Y)="


def to_brf(braille: str, line_length: int = 40, page_lines: int = 25) -> str:
    """Convert Unicode Braille to BRF: wrapped at word boundaries, form feed between pages."""
    lines = []
    for paragraph in braille.split("\n"):
        line = ""
        for word in paragraph.split(BLANK):
            word = "".join(ASCII_BRAILLE[(ord(c) - 0x2800) & 0x3F] for c in word)
            while len(word) > line_length:  # a word longer than a line gets split
                if line:
                    lines.append(line)
                    line = ""
                lines.append(word[:line_length])
                word = word[line_length:]
            if not line:
                line = word
            elif len(line) + 1 + len(word) <= line_length:
                line += " " + word
            else:
                lines.append(line)
                line = word
        lines.append(line)

    pages = [lines[i:i + page_lines] for i in range(0, len(lines), page_lines)] or [[]]
    return "\f".join("\r\n".join(p) + "\r\n" for p in pages)


def from_brf(brf: str) -> str:
    """Convert BRF text back to Unicode Braille (used for checking the export)."""
    out = []
    for ch in brf.replace("\r\n", "\n").replace("\f", ""):
        if ch == "\n":
            out.append("\n")
        else:
            out.append(chr(0x2800 + ASCII_BRAILLE.index(ch.upper())))
    return "".join(out)


def save_txt(braille: str, path) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write(braille + "\n")


def save_brf(braille: str, path) -> None:
    with open(path, "w", encoding="ascii", newline="") as f:
        f.write(to_brf(braille))
