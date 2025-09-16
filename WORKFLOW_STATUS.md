# BrunellaAgentSystem — Fejlesztési Workflow és Státusz (naprakész)

**Dátum:** 2025-09-16

---

## Összefoglaló

- Többrétegű fejlesztések készültek a backend, frontend és DevOps oldalon a helyi fejlesztői élmény és a megbízható futtatás érdekében (Windows + G: meghajtó fókusz).
- Beépült egy kódoló specialista (Ollama/Qwen család), HTTP fallback-kel, valamint egy egyszerű smoke-test endpoint a backendben.
- Docker oldalon BuildKit optimalizációk, repo-lokális cache/volume-ok, és Windows-specifikus javítások készültek; a Docker engine jelenleg nem fut a gépen, ezért a stack indítás validációja még hátra van.

## Végrehajtott tevékenységek (rövid kronológia)

- Dokumentáció és repo-útmutatók
  - `.github/copilot-instructions.md` létrehozva/testreszabva a repo architektúrájára.
  - `report09.15.new.md` frissítve: részletes értékelés + összefoglalás + következő lépések.

- Backend
  - FastAPI `GET /health` hozzáadva (`backend/src/app.py`), egységteszttel támogatva (`backend/tests/test_api.py`).
  - CORS kiegészítve: `http://localhost:5173`, `http://127.0.0.1:5173`, valamint `:3000` a prod frontendre.
  - Kódoló specialista: `backend/src/specialists/coder_agent.py`
    - Elsődlegesen `ChatOllama` (Ollama), dinamikus `base_url` (konténerben `http://host.docker.internal:11434`, lokálisan `http://127.0.0.1:11434`).
    - HTTP fallback implementálva: ha a `langchain_ollama` nem elérhető, közvetlen Ollama REST `/api/generate` hívás.
  - Egyszerű POST endpoint a füstteszthez: `POST /coder/generate` (nyelv + prompt → kód visszaadás).
  - Függőségek: `langchain-ollama` hozzáadva a `backend/pyproject.toml`-hoz (kézi szerkesztés is történt 2025-09-16-án).

- Orchestrator/Tools
  - `backend/src/agent/tools.py`: `research_tool`, `qwen3_coder_tool` bekötve.
  - `backend/src/agent/graph.py`: Gemini 1.5 Pro orchestrator tool-bindingokkal.

- Frontend
  - `VITE_API_URL` támogatás (build arg és környezeti változó) → rugalmas backend elérés (dev 5173, prod 8000/3000).
  - Vite/React alapú UI érintett részei igazítva (App.tsx és típusok kiegészítése).

- DevOps / Docker / Szkriptek
  - `docker-compose.yml`: `extra_hosts` (`host.docker.internal`) és backend healthcheck.
  - Repo-lokális volume-ok (G:): `./docker-data/postgres`, `./docker-data/redis`.
  - BuildKit/buildx cache használat a Dockerfile-okban; PowerShell build-script detektálja a buildx hiányát és visszavált klasszikus buildre.
  - `build-images.ps1`, `run-stack.bat`, `stop-stack.bat`: edzettebb hibatűrés, Compose v2/v1 fallback.

- Lokális futtatás (Docker nélkül)
  - Validált út: venv (3.11) + `pip install -e backend/[dev]` + `uvicorn src.app:app` → `/health` OK.
  - Ollama elérés HTTP-n: `qwen2.5-coder:7b` modell elérhető; `OLLAMA_MODEL` beállítva és használatban.

## Jelenlegi futási állapot

- Docker Desktop engine: jelenleg nem fut (pipe hiba: `open //./pipe/dockerDesktopLinuxEngine`). A stack építés/indítás emiatt blokkolt.
- Backend lokális futtatás: működik, `/health` zöld, `POST /coder/generate` használható.
- Ollama: fut, `qwen2.5-coder:7b` telepítve (a `qwen3:7b` manifeszt nem elérhető volt, ezért váltottunk).

## Ismert problémák és megállapítások

- Docker motor Windows-on leállt/crash-elt; WSL2 és Desktop indítás szükséges (GUI vagy `Start-Service com.docker.service`).
- A shell-ben URL-ek közvetlen beillesztése hiba ("'http:' is not recognized..."); REST hívásokhoz `Invoke-RestMethod` használandó.
- A WindowsApps alatti `python3.13.exe` stub nem megfelelő a projekthez; használj projekt-venv-et (3.11).
- Coder agent Docker-ben a host-hoz csak `host.docker.internal` néven fér hozzá; ezt már biztosítja az `extra_hosts`.

## Következő lépések (prioritási sorrend)

1. Docker engine helyreállítása és stack validáció
   - Indítás: Docker Desktop GUI vagy `Start-Service com.docker.service` → ellenőrzés `docker version`/`docker info`.
   - Ha pipe hiba: `wsl --status`, `wsl -l -v`, `wsl --update`, `wsl --shutdown`, majd Desktop újraindítás.
   - Építés/indítás: `pwsh -NoProfile -File .\build-images.ps1` → `.\run-stack.bat`.
   - Ellenőrzés: `http://127.0.0.1:8000/health`, `http://127.0.0.1:3000`.

2. CRAWL 2. lépés fókusz-ellenőrzés
   - `langchain-ollama` jelen van; `coder_agent.py` base_url logika rendben.
   - Orchestrator → `qwen3_coder_tool` end-to-end próba a stackben, ha Docker fut.

3. Minőségi finomítások (nem blokkoló)
   - Frontend típusok további szigorítása.
   - (Opció) CI füstteszt workflow hozzáadása.

## Gyors parancsok (PowerShell)

```powershell
# Docker indítás és állapot
Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"
Start-Service com.docker.service
docker version
docker info

# Stack build/indítás (repo gyökér)
cd G:\Brunella\projects\BrunellaAgentSystem
$env:DOCKER_BUILDKIT = "1"
pwsh -NoProfile -File .\build-images.ps1
.\run-stack.bat

# Lokális backend (Docker nélkül)
py -3.11 -m venv .venv311
.\.venv311\Scripts\Activate.ps1
pip install -U pip
pip install -e backend/[dev]
$env:OLLAMA_MODEL = "qwen2.5-coder:7b"
cd backend
python -m uvicorn src.app:app --host 127.0.0.1 --port 8000

# Health + coder smoke test
Invoke-RestMethod -Method GET -Uri http://127.0.0.1:8000/health
$body = @{ language="python"; prompt="Írj egy hello_world függvényt, ami 'hello world'-öt ad vissza." } | ConvertTo-Json
Invoke-RestMethod -Method POST -Uri http://127.0.0.1:8000/coder/generate -Body $body -ContentType "application/json"
```

## Környezeti változók

- `GEMINI_API_KEY`: kötelező a kutató ügynökhöz.
- `OLLAMA_MODEL`: alapértelmezettként `qwen2.5-coder:7b` javasolt.

---

Ezt a státuszt folytatáskor érdemes elsőként beolvasni: tartalmazza az aktuális technikai döntéseket, ismert állapotot és a következő lépések sorrendjét.
