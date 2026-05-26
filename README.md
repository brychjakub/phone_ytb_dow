# PythonAnywhere YouTube downloader (web)

Tahle verze je dělaná pro **PythonAnywhere + GitHub + git pull**.

## Co to umí

- web formulář (URL + video/audio + kvalita)
- stažení přes `yt-dlp`
- video do MP4, audio do MP3
- soubory uloží na server do `downloads/`
- rovnou je nabídne ke stažení v prohlížeči

## Struktura

- `app.py` – Flask web aplikace
- `requirements.txt` – závislosti
- `downloads/` – cílová složka pro stažené soubory (vytvoří se automaticky)

## Nasazení na PythonAnywhere (GitHub -> git pull)

### 1) Připoj repo na PythonAnywhere

V Bash konzoli na PythonAnywhere:

```bash
git clone <TVUJ_GITHUB_REPO_URL>
cd <NAZEV_REPA>
```

Pro update později:

```bash
git pull
```

### 2) Virtualenv + instalace

```bash
python3.10 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
```

### 3) ffmpeg na PythonAnywhere

Většinou je `ffmpeg` dostupné systémově. Ověř:

```bash
ffmpeg -version
ffprobe -version
```

Pokud by chybělo, audio MP3 převod nebude fungovat.

### 4) Web app v PythonAnywhere

1. V dashboardu vytvoř **New Web App** (Manual config, Python 3.10).
2. Nastav **Source code** na složku s repem.
3. Nastav **Virtualenv** na `.../<repo>/.venv`.
4. Otevři WSGI soubor a dej tam:

```python
import sys
path = '/home/<uzivatel>/<repo>'
if path not in sys.path:
    sys.path.append(path)

from app import app as application
```

5. Klikni **Reload**.

## Workflow, který jsi chtěl

- upravíš kód lokálně
- push na GitHub
- na PythonAnywhere uděláš:

```bash
cd <repo>
git pull
source .venv/bin/activate
pip install -r requirements.txt
```

- v dashboardu klikneš **Reload**

Hotovo, změny běží online.

## Důležité limity

- stahuj jen obsah, který smíš stahovat
- velká videa mohou timeoutnout
- úložiště na PythonAnywhere je omezené, průběžně maž staré soubory z `downloads/`

## Rychlý lokální test

```bash
python app.py
```

Pak otevři `http://127.0.0.1:8000`.
