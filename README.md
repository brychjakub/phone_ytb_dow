# Pydroid 3 YouTube downloader (Android)

Tento projekt je jednoduchý skript pro **Pydroid 3** v Androidu, který používá `yt-dlp`.

> Používej ho jen na obsah, na který máš právo (vlastní videa, veřejná licence, souhlas autora).

## Co umí

- stáhnout video (MP4)
- stáhnout audio
  - jako MP3 (pokud je dostupné `ffmpeg` + `ffprobe`)
  - nebo "native" audio bez převodu (např. m4a/webm)
- volba kvality videa
- uložit soubory do složky v telefonu

## Instalace v Pydroid 3

1. Otevři Pydroid 3.
2. V terminálu spusť:

```bash
pip install yt-dlp
```

3. Pro převod do MP3 potřebuješ i `ffmpeg` a `ffprobe`.
   Pokud je nemáš, skript stáhne audio v původním formátu bez převodu.

## Spuštění

```bash
python ytb_offline.py
```

## Poznámky

- Některá videa mohou být omezená regionem, přihlášením nebo právy.
- Pokud se mění YouTube API/chování, aktualizuj:

```bash
pip install -U yt-dlp
```
