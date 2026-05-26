#!/usr/bin/env python3
"""Jednoduchý CLI downloader pro Pydroid 3 (Android)."""

from pathlib import Path
import shutil
from typing import Dict, Any

try:
    from yt_dlp import YoutubeDL
except ImportError:
    print("Chybí balíček yt-dlp. Nainstaluj ho: pip install yt-dlp")
    raise SystemExit(1)


def ask(prompt: str, default: str | None = None) -> str:
    if default:
        value = input(f"{prompt} [{default}]: ").strip()
        return value or default
    return input(f"{prompt}: ").strip()


def has_ffmpeg_tools() -> bool:
    return shutil.which("ffmpeg") is not None and shutil.which("ffprobe") is not None


def build_options(mode: str, out_dir: Path, quality: str, extract_mp3: bool) -> Dict[str, Any]:
    opts: Dict[str, Any] = {
        "outtmpl": str(out_dir / "%(title)s.%(ext)s"),
        "noplaylist": True,
        "ignoreerrors": False,
        "quiet": False,
    }

    if mode == "video":
        if quality == "best":
            fmt = "bestvideo+bestaudio/best"
        else:
            fmt = f"bestvideo[height<={quality}]+bestaudio/best[height<={quality}]"

        opts.update(
            {
                "format": fmt,
                "merge_output_format": "mp4",
            }
        )
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

    extract_mp3 = False
    if mode == "audio":
        ffmpeg_ok = has_ffmpeg_tools()
        if ffmpeg_ok:
            choice = ask("Audio formát (mp3/native)", "mp3").lower()
            if choice not in {"mp3", "native"}:
                print("Neplatná volba, použiji 'mp3'.")
                choice = "mp3"
            extract_mp3 = choice == "mp3"
        else:
            print("ffmpeg/ffprobe nebyl nalezen.")
            print("Stáhnu audio v původním formátu (např. m4a/webm) bez převodu do MP3.")

    default_path = "/storage/emulated/0/Download/yt_offline"
    out_dir = Path(ask("Cílová složka", default_path)).expanduser()
    out_dir.mkdir(parents=True, exist_ok=True)

    options = build_options(mode, out_dir, quality, extract_mp3)

    try:
        with YoutubeDL(options) as ydl:
            ydl.download([url])
        print(f"\nHotovo. Soubor je uložen v: {out_dir}")
    except Exception as exc:
        print(f"Chyba při stahování: {exc}")
        print("Tip: aktualizuj yt-dlp. Pokud chceš MP3, doinstaluj ffmpeg i ffprobe.")


if __name__ == "__main__":
    main()
