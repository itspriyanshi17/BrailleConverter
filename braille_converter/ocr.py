"""Read printed text from a photo with EasyOCR."""

import re
import threading

# OCR often reads the danda "।" as "|", "l" or "I". Fix it when it ends a word
# written in a script that uses the danda (Devanagari through Odia).
DANDA_MISREAD = re.compile(r"(?<=[\u0900-\u0B7F])\s?[|lI](?=\s|$)", re.MULTILINE)

# EasyOCR can only combine languages that share a recognition model.
# Each group below can be mixed with English, but not with another group.
OCR_GROUPS = {
    "devanagari": {"hi", "mr", "ne"},
    "bengali": {"bn", "as"},
    "tamil": {"ta"},
    "telugu": {"te"},
    "kannada": {"kn"},
}
SUPPORTED = {"en"} | set().union(*OCR_GROUPS.values())


def check_languages(langs: list[str]) -> list[str]:
    langs = list(dict.fromkeys(["en", *langs]))
    unsupported = [l for l in langs if l not in SUPPORTED]
    if unsupported:
        raise ValueError(
            f"OCR does not support: {', '.join(unsupported)}. Supported: {', '.join(sorted(SUPPORTED))}. "
            "(Gujarati, Punjabi, Odia and Malayalam can still be converted with --text.)"
        )
    groups = {g for l in langs for g, members in OCR_GROUPS.items() if l in members}
    if len(groups) > 1:
        raise ValueError(
            f"These languages cannot be read in one pass: {', '.join(langs)}. "
            "Pick languages from one script (e.g. hi+mr, or bn, or ta), plus English."
        )
    return langs


def _load_image(source):
    """Open a file path or raw image bytes, upright (phone photos store rotation in EXIF)."""
    import io

    import numpy as np
    from PIL import Image, ImageOps, UnidentifiedImageError

    try:
        img = Image.open(io.BytesIO(source) if isinstance(source, bytes) else source)
        img = ImageOps.exif_transpose(img).convert("L")
    except (UnidentifiedImageError, OSError) as e:
        raise ValueError("Could not open the image. Use a JPG, PNG or WEBP photo.") from e
    return np.array(img)


def _preprocess(source):
    import cv2

    gray = _load_image(source)
    # Enlarge small images so letters have enough pixels; shrink huge phone photos for speed.
    h, w = gray.shape
    if max(h, w) < 2400 or max(h, w) > 3000:
        target = 2400 if max(h, w) < 2400 else 3000
        scale = target / max(h, w)
        gray = cv2.resize(gray, None, fx=scale, fy=scale,
                          interpolation=cv2.INTER_CUBIC if scale > 1 else cv2.INTER_AREA)
    gray = cv2.fastNlMeansDenoising(gray, h=10)
    gray = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(gray)
    return gray


def _join_lines(results) -> str:
    """Put detected words back into reading order: top-to-bottom lines, left-to-right."""
    boxes = []
    for bbox, text, _conf in results:
        ys = [p[1] for p in bbox]
        xs = [p[0] for p in bbox]
        boxes.append((min(ys), max(ys), min(xs), text))
    boxes.sort()

    lines = []  # each: [top, bottom, [(x, text)]]
    for top, bottom, x, text in boxes:
        centre = (top + bottom) / 2
        for line in lines:
            if line[0] <= centre <= line[1]:
                line[2].append((x, text))
                line[0], line[1] = min(line[0], top), max(line[1], bottom)
                break
        else:
            lines.append([top, bottom, [(x, text)]])
    return "\n".join(" ".join(t for _, t in sorted(words)) for _, _, words in lines)


_readers = {}
_lock = threading.Lock()


def _reader(langs: tuple[str, ...], gpu: bool):
    """Loading a model takes seconds, so keep one reader per language set."""
    import easyocr
    import torch

    key = (langs, gpu)
    if key not in _readers:
        _readers[key] = easyocr.Reader(list(langs), gpu=gpu and torch.cuda.is_available(), verbose=False)
    return _readers[key]


def _ocr(image, langs: tuple[str, ...], gpu: bool) -> tuple[str, float]:
    """Run one OCR pass. Returns the text and its confidence (0-1, weighted by text length)."""
    import torch

    with _lock:  # one OCR job at a time; the models are shared
        try:
            results = _reader(langs, gpu).readtext(image, paragraph=False)
        except torch.OutOfMemoryError:
            # The GPU is full (another program, or a huge photo): finish this one on the CPU.
            torch.cuda.empty_cache()
            results = _reader(langs, False).readtext(image, paragraph=False)
    chars = sum(len(t) for _, t, _ in results)
    confidence = float(sum(c * len(t) for _, t, c in results) / chars) if chars else 0.0
    return DANDA_MISREAD.sub("\u0964", _join_lines(results)), confidence


def read_text(source, langs: list[str], gpu: bool = True) -> str:
    """Read text from an image file path or raw image bytes."""
    langs = check_languages(langs)
    return _ocr(_preprocess(source), tuple(langs), gpu)[0]


AUTO_CANDIDATES = [[], ["hi"]]  # English only, Hindi + English
LOW_CONFIDENCE = 0.4


def read_photo(source, lang: str | None = None, gpu: bool = True) -> tuple[str, str, float]:
    """Read a photo for the website. lang=None tries each AUTO_CANDIDATES set and keeps
    the result OCR is most confident about (the wrong language scores far lower).
    Returns (text, language used, confidence 0-1)."""
    image = _preprocess(source)
    candidates = AUTO_CANDIDATES if lang is None else [[lang] if lang != "en" else []]
    results = []
    for c in candidates:
        text, confidence = _ocr(image, tuple(check_languages(c)), gpu)
        results.append((confidence, text, c[0] if c else "en"))
    confidence, text, used = max(results)
    return text, used, confidence
