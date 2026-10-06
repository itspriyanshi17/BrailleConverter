"""Split mixed text by script and send each piece to the right Braille table."""

import unicodedata
from dataclasses import dataclass, field

from . import bharati, english
from .cells import UNKNOWN


@dataclass
class Result:
    units: list[tuple[str, str]]  # (printed source, braille cells)
    unknown: list[str] = field(default_factory=list)

    @property
    def braille(self) -> str:
        return "".join(cells for _, cells in self.units)


def _runs(text: str):
    """Yield (is_indic, chunk). Spaces and punctuation go with the Latin side."""
    start, current = 0, None
    for i, ch in enumerate(text):
        indic = bharati.script_of(ch) is not None or (current and ch in bharati.ZERO_WIDTH)
        indic = bool(indic)
        if current is None:
            current = indic
        elif indic != current:
            yield current, text[start:i]
            start, current = i, indic
    if current is not None:
        yield current, text[start:]


def to_braille(text: str) -> Result:
    text = unicodedata.normalize("NFC", text)
    units: list[tuple[str, str]] = []
    for indic, chunk in _runs(text):
        units += bharati.translate(chunk) if indic else english.translate(chunk)
    unknown = sorted({src for src, cells in units if cells == UNKNOWN and src.strip()})
    return Result(units, unknown)
