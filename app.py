#!/usr/bin/env python3
"""Web version of the Braille converter.

Run:  .venv/bin/python app.py
Then open http://localhost:5000 (or the network address it prints, from a phone on the same Wi-Fi).
"""

import io
import socket

from flask import Flask, jsonify, render_template, request, send_file

from braille_converter import to_braille
from braille_converter.export import to_brf
from braille_converter.ocr import LOW_CONFIDENCE, read_photo
from braille_converter.render import save_png

MAX_TEXT = 20_000

LANGUAGES = [
    ("auto", "Auto-detect (English / Hindi)"),
    ("en", "English"),
    ("hi", "Hindi + English"),
    ("mr", "Marathi + English"),
    ("ne", "Nepali + English"),
    ("bn", "Bengali + English"),
    ("as", "Assamese + English"),
    ("ta", "Tamil + English"),
    ("te", "Telugu + English"),
    ("kn", "Kannada + English"),
]

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 20 * 1024 * 1024  # photos up to 20 MB


def _text_from_request() -> str:
    text = (request.get_json(silent=True) or {}).get("text", "")
    if not isinstance(text, str):
        raise ValueError("text must be a string")
    if len(text) > MAX_TEXT:
        raise ValueError(f"Text is too long (max {MAX_TEXT:,} characters).")
    return text


@app.get("/")
def index():
    return render_template("index.html", languages=LANGUAGES)


@app.post("/api/ocr")
def ocr():
    photo = request.files.get("image")
    if not photo:
        return jsonify(error="No photo was uploaded."), 400
    lang = request.form.get("lang", "auto")
    try:
        text, used, confidence = read_photo(photo.read(), None if lang == "auto" else lang)
    except ValueError as e:
        return jsonify(error=str(e)), 400
    names = dict(LANGUAGES)
    return jsonify(
        text=text,
        language=names.get(used, used).replace(" + English", ""),
        confidence=round(confidence, 2),
        low_confidence=confidence < LOW_CONFIDENCE,
    )


@app.post("/api/convert")
def convert():
    try:
        text = _text_from_request()
    except ValueError as e:
        return jsonify(error=str(e)), 400
    result = to_braille(text)
    return jsonify(
        braille=result.braille,
        units=result.units,
        unknown=result.unknown,
        brf=to_brf(result.braille),
    )


@app.post("/api/png")
def png():
    try:
        text = _text_from_request()
    except ValueError as e:
        return jsonify(error=str(e)), 400
    buf = io.BytesIO()
    save_png(to_braille(text).units, buf)
    buf.seek(0)
    return send_file(buf, mimetype="image/png", as_attachment=True, download_name="braille.png")


@app.errorhandler(413)
def too_large(_e):
    return jsonify(error="That photo is too big (max 20 MB)."), 413


def _lan_ip() -> str | None:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("10.255.255.255", 1))  # no packet is sent; just picks the outgoing interface
            return s.getsockname()[0]
    except OSError:
        return None


if __name__ == "__main__":
    port = 5000
    print(f"\n  On this computer:  http://localhost:{port}")
    if ip := _lan_ip():
        print(f"  On your phone (same Wi-Fi):  http://{ip}:{port}\n")
    app.run(host="0.0.0.0", port=port, threaded=True)
