#!/usr/bin/env python3
"""YouTube downloader helper for Pydroid 3 (Android) using yt-dlp."""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path
from typing import Any, Dict

try:
    from yt_dlp import YoutubeDL
except ImportError:
    print("Chybí balíček yt-dlp. Nainstaluj ho: pip install -U yt-dlp")
    raise SystemExit(1)


def ask(prompt: str, default: str | None = None) -> str:
    if default is not None:
        value = input(f"{prompt} [{default}]: ").strip()
        return value or default
    return input(f"{prompt}: ").strip()


def is_executable_ok(path: str) -> bool:
    try:
        result = subprocess.run(
            [path, "-version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
        return result.returncode == 0
    except Exception:
        return False


def get_exec_version(path: str) -> str:
    try:
        result = subprocess.run(
            [path, "-version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
        line = (result.stdout or result.stderr).splitlines()
        return line[0] if line else "(verze nezjištěna)"
    except Exception as exc:
        return f"(chyba zjištění verze: {exc})"


def resolve_ffmpeg_location(interactive: bool = True) -> str | None:
    ffmpeg_path = shutil.which("ffmpeg")
    ffprobe_path = shutil.which("ffprobe")

    if (
        ffmpeg_path
        and ffprobe_path
        and is_executable_ok(ffmpeg_path)
        and is_executable_ok(ffprobe_path)
    ):
        return str(Path(ffmpeg_path).parent)

    if not interactive:
        return None

    print("\n⚠️ ffmpeg/ffprobe nebyl nalezen v PATH nebo není spustitelný.")
    custom = ask("Zadej cestu ke složce s ffmpeg+ffprobe (ENTER = přeskočit)", "").strip()
    if not custom:
        return None

    base = Path(custom).expanduser()
    ffmpeg_file = base / "ffmpeg"
    ffprobe_file = base / "ffprobe"

    if (
        ffmpeg_file.exists()
        and ffprobe_file.exists()
        and is_executable_ok(str(ffmpeg_file))
        and is_executable_ok(str(ffprobe_file))
    ):
        return str(base)

    print("Zadaná cesta neobsahuje funkční ffmpeg + ffprobe. Použiji fallback bez MP3 převodu.")
    return None


def print_diagnostics() -> None:
    print("\n=== DIAGNOSTIKA PRO PYDROID / yt-dlp / ffmpeg ===")
    print(f"Python executable: {shutil.which('python') or '(nenalezeno v PATH)'}")
    print(f"Aktuální pracovní složka: {Path.cwd()}")
    print(f"HOME: {os.environ.get('HOME', '(nenastaveno)')}")
    print(f"PATH: {os.environ.get('PATH', '(nenastaveno)')}")

    ffmpeg_path = shutil.which("ffmpeg")
    ffprobe_path = shutil.which("ffprobe")
    print(f"ffmpeg v PATH: {ffmpeg_path or '(nenalezeno)'}")
    print(f"ffprobe v PATH: {ffprobe_path or '(nenalezeno)'}")

    if ffmpeg_path:
        print(f"ffmpeg verze: {get_exec_version(ffmpeg_path)}")
    if ffprobe_path:
        print(f"ffprobe verze: {get_exec_version(ffprobe_path)}")

    try:
        import yt_dlp

        print(f"yt-dlp verze: {yt_dlp.version.__version__}")
    except Exception as exc:
        print(f"yt-dlp verze: nelze zjistit ({exc})")

    detected = resolve_ffmpeg_location(interactive=False)
    print(f"resolve_ffmpeg_location(interactive=False): {detected or '(nenalezeno)'}")
    print("=== KONEC DIAGNOSTIKY ===\n")


def build_options(
    mode: str,
    out_dir: Path,
    quality: str,
    extract_mp3: bool,
    ffmpeg_location: str | None,
) -> Dict[str, Any]:
    opts: Dict[str, Any] = {
        "outtmpl": str(out_dir / "%(title)s.%(ext)s"),
        "noplaylist": True,
        "ignoreerrors": False,
        "quiet": False,
    }

    if ffmpeg_location:
        opts["ffmpeg_location"] = ffmpeg_location

    if mode == "video":
        if quality == "best":
            fmt = "bestvideo+bestaudio/best"
        else:
            fmt = f"bestvideo[height<={quality}]+bestaudio/best[height<={quality}]"

        opts.update({"format": fmt, "merge_output_format": "mp4"})
    else:
        opts["format"] = "bestaudio/best"
        if extract_mp3:
            opts["postprocessors"] = [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }
            ]

    return opts


def main() -> None:
    print("=== YouTube offline downloader pro Pydroid 3 ===")
    print("Používej jen pro obsah, který smíš stahovat.\n")

    show_diag = ask("Chceš vypsat diagnostiku prostředí? (ano/ne)", "ano").lower()
    if show_diag in {"ano", "a", "yes", "y"}:
        print_diagnostics()

    url = ask("Vlož URL videa")
    if not url:
        print("URL je prázdná. Konec.")
        return

    mode = ask("Režim (video/audio)", "video").lower()
    if mode not in {"video", "audio"}:
        print("Neplatný režim, použiji 'video'.")
        mode = "video"

    quality = "best"
    if mode == "video":
        quality = ask("Kvalita (best, 1080, 720, 480)", "best")
        if quality not in {"best", "1080", "720", "480"}:
            print("Neplatná kvalita, použiji 'best'.")
            quality = "best"

    ffmpeg_location = resolve_ffmpeg_location(interactive=True)
    print(f"Použitá ffmpeg_location: {ffmpeg_location or '(žádná)'}")

    extract_mp3 = False
    if mode == "audio":
        if ffmpeg_location:
            choice = ask("Audio formát (mp3/native)", "mp3").lower()
            if choice not in {"mp3", "native"}:
                print("Neplatná volba, použiji 'mp3'.")
                choice = "mp3"
            extract_mp3 = choice == "mp3"
        else:
            print("Stáhnu audio v původním formátu (např. m4a/webm) bez převodu do MP3.")

    default_path = "/storage/emulated/0/Download/yt_offline"
    out_dir = Path(ask("Cílová složka", default_path)).expanduser()
    out_dir.mkdir(parents=True, exist_ok=True)

    options = build_options(mode, out_dir, quality, extract_mp3, ffmpeg_location)
    print(f"\nShrnutí voleb: mode={mode}, quality={quality}, extract_mp3={extract_mp3}, out_dir={out_dir}")

    try:
        with YoutubeDL(options) as ydl:
            ydl.download([url])
        print(f"\nHotovo. Soubor je uložen v: {out_dir}")
    except Exception as exc:
        print(f"Chyba při stahování: {exc}")
        print("Tip: aktualizuj yt-dlp. Pokud chceš MP3, zadej funkční cestu k ffmpeg+ffprobe.")


if __name__ == "__main__":
    main()
