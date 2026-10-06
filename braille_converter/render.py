"""Show Braille as dot cells: in the terminal (●/○) and as a PNG image."""

import shutil
import unicodedata
from pathlib import Path

from .bharati import script_of
from .cells import raised_dots

FILLED, EMPTY = "●", "○"
# Dot number at each (row, column) of the 3x2 cell.
LAYOUT = [(1, 4), (2, 5), (3, 6)]

FONT_DIRS = [Path("/usr/share/fonts/truetype/noto"), Path("/usr/share/fonts/truetype/dejavu"),
             Path("/usr/share/fonts/noto"), Path("/usr/share/fonts/TTF")]
SCRIPT_FONTS = {
    "devanagari": "NotoSansDevanagari-Regular.ttf",
    "bengali": "NotoSansBengali-Regular.ttf",
    "gurmukhi": "NotoSansGurmukhi-Regular.ttf",
    "gujarati": "NotoSansGujarati-Regular.ttf",
    "oriya": "NotoSansOriya-Regular.ttf",
    "tamil": "NotoSansTamil-Regular.ttf",
    "telugu": "NotoSansTelugu-Regular.ttf",
    "kannada": "NotoSansKannada-Regular.ttf",
    "malayalam": "NotoSansMalayalam-Regular.ttf",
    None: "DejaVuSans.ttf",
}


def _display_width(s: str) -> int:
    """Rough terminal width: combining marks and zero-width characters take no space."""
    return sum(0 if unicodedata.category(c) in ("Mn", "Me", "Cf") else 1 for c in s)


def _lines(units):
    """Split units at newlines."""
    line = []
    for src, cells in units:
        if cells == "\n":
            yield line
            line = []
        else:
            line.append((src, cells))
    yield line


def terminal_cells(units, width: int | None = None) -> str:
    """Draw each Braille cell as a 3x2 grid of ●/○ with the printed letter underneath."""
    width = width or shutil.get_terminal_size((100, 24)).columns
    blocks = []
    for line in _lines(units):
        rows = ["", "", "", ""]
        used = 0
        for src, cells in line:
            unit_width = 3 * len(cells)
            if used and used + unit_width > width:
                blocks.append("\n".join(r.rstrip() for r in rows))
                rows, used = ["", "", "", ""], 0
            for c in cells:
                raised = raised_dots(c)
                for r, (left, right) in enumerate(LAYOUT):
                    rows[r] += (FILLED if left in raised else EMPTY) + (FILLED if right in raised else EMPTY) + " "
            label = "" if src.isspace() else src
            rows[3] += label + " " * max(unit_width - _display_width(label), 1)
            used += unit_width
        blocks.append("\n".join(r.rstrip() for r in rows))
    return "\n\n".join(blocks)


def _font(script, size):
    from PIL import ImageFont

    for name in (SCRIPT_FONTS.get(script), SCRIPT_FONTS[None]):
        for d in FONT_DIRS:
            if name and (d / name).exists():
                return ImageFont.truetype(str(d / name), size)
    return ImageFont.load_default(size)


def save_png(units, path, cells_per_row: int = 24, title: str | None = None) -> None:
    """Draw the Braille as an image: dot cells with the printed letter below each one."""
    from PIL import Image, ImageDraw

    dot_r, dot_gap = 7, 22            # dot radius, distance between dot centres
    cell_w, cell_h = 2 * dot_gap + 14, 3 * dot_gap + 8
    label_h, row_gap, margin = 40, 26, 30

    # Lay units out into rows, wrapping between words (a word only splits if it
    # is longer than a whole row).
    rows, row = [], []
    for line in _lines(units):
        words, word = [], []
        for unit in line:
            word.append(unit)
            if unit[0].isspace():
                words.append(word)
                word = []
        words.append(word)
        for word in words:
            if row and sum(len(c) for _, c in row) + sum(len(c) for _, c in word) > cells_per_row:
                rows.append(row)
                row = []
            for unit in word:
                if row and sum(len(c) for _, c in row) + len(unit[1]) > cells_per_row:
                    rows.append(row)
                    row = []
                row.append(unit)
        rows.append(row)
        row = []
    rows = [r for r in rows if r] or [[]]

    title_h = 50 if title else 0
    width = 2 * margin + cells_per_row * cell_w
    height = 2 * margin + title_h + len(rows) * (cell_h + label_h + row_gap)
    img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(img)
    if title:
        draw.text((margin, margin), title, fill="#222", font=_font(None, 26))

    y = margin + title_h
    for row in rows:
        x = margin
        for src, cells in row:
            unit_x = x
            for c in cells:
                raised = raised_dots(c)
                for r, (left, right) in enumerate(LAYOUT):
                    for col, dot in enumerate((left, right)):
                        cx = x + 7 + dot_r + col * dot_gap
                        cy = y + 4 + dot_r + r * dot_gap
                        box = (cx - dot_r, cy - dot_r, cx + dot_r, cy + dot_r)
                        if dot in raised:
                            draw.ellipse(box, fill="#111")
                        else:
                            draw.ellipse(box, outline="#bbb", width=2)
                x += cell_w
            if not src.isspace():
                script = next((script_of(ch) for ch in src if script_of(ch)), None)
                font = _font(script, 28)
                text_w = draw.textlength(src, font=font)
                draw.text((unit_x + (x - unit_x - text_w) / 2, y + cell_h), src, fill="#1a56db", font=font)
            if len(cells) > 1:  # bracket cells that belong to one printed letter
                draw.line((unit_x + 4, y + cell_h + 2, x - 10, y + cell_h + 2), fill="#9db4e8", width=2)
        y += cell_h + label_h + row_gap
    img.save(path, format="PNG")
