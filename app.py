#!/usr/bin/env python3
"""Web downloader for PythonAnywhere using yt-dlp."""

from __future__ import annotations

import os
import subprocess
import uuid
from pathlib import Path

from flask import Flask, redirect, render_template_string, request, send_from_directory, url_for

BASE_DIR = Path(__file__).resolve().parent
DOWNLOAD_DIR = BASE_DIR / "downloads"
DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024

HTML = """
<!doctype html>
<html lang="cs">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>YT Downloader (PythonAnywhere)</title>
  <style>
    body { font-family: Arial, sans-serif; max-width: 760px; margin: 2rem auto; padding: 0 1rem; }
    label { display:block; margin-top: 0.75rem; font-weight: 600; }
    input, select, button { width: 100%; padding: 0.6rem; margin-top:0.2rem; }
    .ok { padding: 0.7rem; background: #eafbe7; border:1px solid #8fd48a; margin: 1rem 0; }
    .err { padding: 0.7rem; background: #ffefef; border:1px solid #de8c8c; margin: 1rem 0; white-space: pre-wrap; }
    .hint { font-size: 0.92rem; color: #444; }
    ul { padding-left: 1.1rem; }
  </style>
</head>
<body>
  <h1>YT Downloader (PythonAnywhere)</h1>
  <p class="hint">Používej jen obsah, který smíš stahovat.</p>

  {% if message %}<div class="ok">{{ message|safe }}</div>{% endif %}
  {% if error %}<div class="err">{{ error }}</div>{% endif %}

  <form method="post" action="{{ url_for('download') }}">
    <label for="url">YouTube URL</label>
    <input id="url" name="url" required placeholder="https://www.youtube.com/watch?v=..." />

    <label for="mode">Režim</label>
    <select id="mode" name="mode">
      <option value="video">Video (MP4)</option>
      <option value="audio">Audio (MP3)</option>
    </select>

    <label for="quality">Kvalita videa</label>
    <select id="quality" name="quality">
      <option value="best">best</option>
      <option value="1080">1080</option>
      <option value="720">720</option>
      <option value="480">480</option>
    </select>

    <button type="submit">Stáhnout</button>
  </form>

  <h2>Poslední soubory</h2>
  <ul>
    {% for f in files %}
      <li><a href="{{ url_for('file_download', filename=f) }}">{{ f }}</a></li>
    {% else %}
      <li>Zatím nic.</li>
    {% endfor %}
  </ul>
</body>
</html>
"""


def build_command(url: str, mode: str, quality: str, output_template: str) -> list[str]:
    cmd = ["yt-dlp", "--no-playlist", "-o", output_template]

    if mode == "audio":
        cmd += ["-f", "bestaudio/best", "-x", "--audio-format", "mp3", "--audio-quality", "192K"]
    else:
        if quality == "best":
            fmt = "bestvideo+bestaudio/best"
        else:
            fmt = f"bestvideo[height<={quality}]+bestaudio/best[height<={quality}]"
        cmd += ["-f", fmt, "--merge-output-format", "mp4"]

    cmd.append(url)
    return cmd


def recent_files(limit: int = 20) -> list[str]:
    files = [p for p in DOWNLOAD_DIR.iterdir() if p.is_file()]
    files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return [p.name for p in files[:limit]]


@app.get("/")
def index():
    return render_template_string(HTML, message=None, error=None, files=recent_files())


@app.post("/download")
def download():
    url = (request.form.get("url") or "").strip()
    mode = (request.form.get("mode") or "video").strip().lower()
    quality = (request.form.get("quality") or "best").strip()

    if not url:
        return render_template_string(HTML, message=None, error="URL je povinná.", files=recent_files())

    if mode not in {"video", "audio"}:
        mode = "video"
    if quality not in {"best", "1080", "720", "480"}:
        quality = "best"

    uniq = uuid.uuid4().hex[:8]
    outtmpl = str(DOWNLOAD_DIR / f"%(title).120s_{uniq}.%(ext)s")
    cmd = build_command(url, mode, quality, outtmpl)

    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, check=False, timeout=1800)
    except FileNotFoundError:
        err = "yt-dlp není dostupné v prostředí. Zkontroluj virtualenv a instalaci requirements.txt"
        return render_template_string(HTML, message=None, error=err, files=recent_files())
    except subprocess.TimeoutExpired:
        err = "Download timeout (30 minut). Zkus kratší video nebo nižší kvalitu."
        return render_template_string(HTML, message=None, error=err, files=recent_files())

    if proc.returncode != 0:
        details = (proc.stderr or proc.stdout or "Neznámá chyba").strip()
        return render_template_string(
            HTML,
            message=None,
            error=f"yt-dlp skončilo chybou:\n{details}",
            files=recent_files(),
        )

    return redirect(url_for("done"))


@app.get("/done")
def done():
    return render_template_string(
        HTML,
        message="Hotovo. Soubor je v seznamu níže.",
        error=None,
        files=recent_files(),
    )


@app.get("/files/<path:filename>")
def file_download(filename: str):
    return send_from_directory(DOWNLOAD_DIR, filename, as_attachment=True)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8000"))
    app.run(host="0.0.0.0", port=port, debug=True)
