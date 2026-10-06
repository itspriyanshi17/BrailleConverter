#!/usr/bin/env python3
"""Convert a photo of printed text (or typed text) into Braille.

Examples:
  python braille.py page.jpg
  python braille.py hindi_page.jpg --lang hi --cells --png out.png
  python braille.py --text "Hello नमस्ते" --cells --txt out.txt --brf out.brf
"""

import argparse
import sys

from braille_converter import to_braille
from braille_converter.export import save_brf, save_txt
from braille_converter.render import save_png, terminal_cells


def main() -> int:
    p = argparse.ArgumentParser(description="Photo / text to Braille (English + Bharati Braille).")
    p.add_argument("image", nargs="?", help="photo of a page or any printed text")
    p.add_argument("--text", help="translate this text instead of reading a photo")
    p.add_argument("--lang", nargs="+", default=[], metavar="CODE",
                   help="languages in the photo besides English: hi mr ne bn as ta te kn")
    p.add_argument("--cells", action="store_true", help="show each letter as a dot cell in the terminal")
    p.add_argument("--png", metavar="FILE", help="save the dot cells as an image")
    p.add_argument("--txt", metavar="FILE", help="save Unicode Braille text")
    p.add_argument("--brf", metavar="FILE", help="save embosser-ready Braille (BRF)")
    p.add_argument("--cpu", action="store_true", help="run OCR on the CPU even if a GPU is available")
    args = p.parse_args()

    if bool(args.image) == bool(args.text):
        p.error("give either an image or --text")

    if args.text:
        text = args.text
    else:
        from braille_converter.ocr import read_text

        print("Reading text from the photo (the first run downloads the OCR models)...", file=sys.stderr)
        try:
            text = read_text(args.image, args.lang, gpu=not args.cpu)
        except ValueError as e:
            p.error(str(e))
        if not text.strip():
            print("No text found in the photo.", file=sys.stderr)
            return 1

    result = to_braille(text)

    print("── Text ──")
    print(text)
    print("\n── Braille ──")
    print(result.braille)
    if args.cells:
        print("\n── Cells ──")
        print(terminal_cells(result.units))
    if result.unknown:
        print(f"\nWarning: no Braille for {' '.join(result.unknown)} (shown as ⠿)", file=sys.stderr)

    if args.txt:
        save_txt(result.braille, args.txt)
        print(f"\nSaved {args.txt}")
    if args.brf:
        save_brf(result.braille, args.brf)
        print(f"Saved {args.brf}")
    if args.png:
        save_png(result.units, args.png)
        print(f"Saved {args.png}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
