# Braille Converter

Take a photo of a book page (or any printed text). The tool reads the text and shows it in Braille.

- **English**: Unified English Braille, Grade 1 (letter by letter).
- **Indian languages**: Bharati Braille. Supported scripts are Hindi/Marathi/Nepali (Devanagari), Bengali/Assamese, Tamil, Telugu, and Kannada. Gujarati, Punjabi, Odia, and Malayalam can be converted from typed text with `--text`, but EasyOCR cannot read them from photos.

## Setup

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

The first run of each language downloads its OCR model (~100 MB).

## Website

```bash
.venv/bin/python app.py
```

Open **http://localhost:5000** on this computer. To use it on your phone, connect the phone to the same Wi-Fi and open the network address the app prints (like `http://192.168.x.x:5000`). On the phone, **Take photo** opens the camera.

How to use it:
1. Take a photo of a page or upload one. You can also switch to **Type text**. **Auto-detect** tries English and Hindi and keeps whichever reads better. For other languages, pick the language yourself. If a photo is hard to read, the page warns you.
2. Check the text it read, and fix any mistakes. The Braille updates as you type.
3. See the Braille text and the dot cells, then copy them or download a .txt, .brf or .png file.

A link like `http://localhost:5000/?text=Hello` opens with that text already converted.

## Command line

```bash
.venv/bin/python braille.py page.jpg                         # English photo
.venv/bin/python braille.py page.jpg --lang hi --cells       # Hindi + English, with dot cells
.venv/bin/python braille.py page.jpg --lang ta --png out.png # Tamil, save cells as an image
.venv/bin/python braille.py --text "Hello नमस्ते" --txt out.txt --brf out.brf
```

| Option | What it does |
|---|---|
| `--lang hi` | Other languages in the photo (`hi mr ne`, `bn as`, `ta`, `te`, `kn`). Pick one script group per run. |
| `--cells` | Print each Braille cell as a ●/○ grid with the printed letter underneath. |
| `--png FILE` | Save the dot cells, labelled with the letters, as an image. |
| `--txt FILE` | Save Unicode Braille text (⠓⠑⠇⠇⠕). |
| `--brf FILE` | Save BRF, an ASCII Braille file that Braille embossers can print (40 cells per line, 25 lines per page). |
| `--cpu` | Run OCR on the CPU even if a GPU is available. |

Tips for good photos: use even lighting, keep the page flat, and make sure the text fills most of the frame.

## Tests

```bash
.venv/bin/python -m pytest
```
