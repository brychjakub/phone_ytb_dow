# Pydroid 3 YouTube downloader (Android)

Tento projekt je jednoduchý skript pro **Pydroid 3** v Androidu, který používá `yt-dlp`.

> Používej ho jen na obsah, na který máš právo (vlastní videa, veřejná licence, souhlas autora).

## Co umí

- stáhnout video (MP4)
- stáhnout audio (MP3)
- volba kvality
- uložit soubory do složky v telefonu

## Instalace v Pydroid 3

1. Otevři Pydroid 3.
2. V terminálu spusť:

```bash
pip install yt-dlp
```

3. Pokud chceš převod do MP3, je potřeba i `ffmpeg` dostupné v systému (v Pydroidu dle možností zařízení/pluginů).

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
