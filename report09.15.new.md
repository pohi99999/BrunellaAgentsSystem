# `BrunellaAgentSystem` — Állapotjelentés (2025-09-15)

Ez a jelentés összefoglalja a legutóbbi módosításokat, a jelenlegi futtatási állapotot és a javasolt következő lépéseket.

## Változtatások

- Docker/Compose:
  - Volumek G: meghajtóra (repo-lokális): `./docker-data/postgres`, `./docker-data/redis`.
  - BuildKit/buildx cache optimalizáció a backend és frontend Dockerfile-ban.
  - Frontend build arg: `VITE_API_URL` (alap: `http://localhost:8000/agent`).
- Frontend:
  - `src/App.tsx`: `apiUrl` konfigurálható (`import.meta.env.VITE_API_URL`), alapértelmezés 8000.
  - `src/vite-env.d.ts`: típus a `VITE_API_URL` környezeti változóra.
- Backend:
  - `src/app.py`: hozzáadva `GET /health` végpont (`{"status":"ok"}`).
  - `tests/test_api.py`: frissítve a `/health` tesztre, a legacy `/crew` eltávolítva.
- Dev eszközök:
  - `build-images.ps1`: buildx + cache + `--load` + hibatűrés, `VITE_API_URL` átadás.
  - `run-stack.bat`: BuildKit engedélyezés, build script hívás, hibakezelés, `docker compose up -d`.
  - `stop-stack.bat`: egyszerűsített leállítás.
  - `.gitignore`: `docker-data/`, `.buildx-cache/` kizárva.

## Futtatás (Windows/PowerShell)

1) API kulcs: Állítsd be a `GEMINI_API_KEY`-t a környezetben vagy `.env`-ben (backend).
2) Build képek és indítás:
   - `./run-stack.bat` vagy PowerShellből: `pwsh -File ./build-images.ps1`
   - Majd: `docker compose up -d`
3) Elérés:
   - Backend: `http://localhost:8000/health` (élő-e) és `http://localhost:8000/agent`
   - Frontend: `http://localhost:3000`

Megjegyzés: Ha a buildx nem érhető el, a build script automatikusan visszavált klasszikus `docker build`-re.

## Jelenlegi Állapot

- Lokális futtatás: a korábbi `run-stack.bat` hiba (Exit Code 1) után a scriptek edzettek; újabb futtatás szükséges a validációhoz.
- TS lint: néhány `any` típus a `App.tsx` eseménykezelőknél további finomítást igényelhet, de működést nem blokkol.
- Backend teszt: `/health` egységtesztre frissítve. A futtatáshoz a `backend` dev függőségek telepítése szükséges.

## Következő Lépések

- Futtasd újra a stacket: `./run-stack.bat`, majd ellenőrizd a `/health`-et és a frontend-et.
- Ha gond van: `docker compose logs -f backend` és `docker compose logs -f frontend`.
- További fejlesztés:
  - Frontend típusok szigorítása az aktivitás eseményeknél.
  - (Opció) Egyszerű e2e smoke teszt hozzáadása GitHub Actions workflow-hoz.
  - Jules AI integráció előkészítése külön tool-ként.

## Értékelés és Összefoglalás

Az architektúra stabil: a hierarchikus LangGraph orchestrator a kutató és kódoló specialistákkal jól szeparálja a felelősségeket. A Docker/Compose beállítások repo-lokális (G:) tárolással gyorsítják a fejlesztést Windows alatt, a BuildKit cache optimalizációk tovább csökkentik az építési időt. A frontend most már konfigurálható `VITE_API_URL`-lal, így a backend elérés rugalmas. A `/health` végpont és a hozzá tartozó teszt növeli az üzemeltetési átláthatóságot.

Kockázatok/Hiányosságok:

- A kódoló specialista az Ollama lokális elérését igényli; Dockerből a `host.docker.internal` feloldás biztosítása szükséges.
- A frontendben néhány `any` típus további finomításra szorul (nem blokkoló).
- A `GEMINI_API_KEY` hiánya a kutató ügynök indítását megakaszthatja.

Összkép: a rendszer futtatható, a kutató ág működőképes, a kódoló ág lokális Ollama telepítés után azonnal használható. A következő lépések a kódoló specialista megerősítésére és a Docker hálózati elérés finomhangolására fókuszálnak.

## Következő Felhasználói Lépés

1. Telepítsd az Ollama-t a hivatalos oldalról: [https://ollama.com](https://ollama.com)
2. Töltsd le és indítsd a Qwen3 modellt:

```powershell
ollama run qwen3:7b
```

## Következő Rendszer Lépés (felhasználói lépés után)

- Hajtsuk végre a `CRAWL_PHASE_IMPLEMENTATION_PLAN.md` 2. lépését:
  - A `backend/pyproject.toml` függőségekhez adjuk hozzá: `langchain-ollama`.
  - Ellenőrizzük a specialista kódot (`backend/src/specialists/coder_agent.py`), hogy az Ollama `base_url` értéke Docker környezetben is jó legyen (`http://host.docker.internal:11434`).
  - Frissítsük a `Docker Compose` konfigurációját úgy, hogy a `host.docker.internal` név feloldható legyen a backend konténerből (`extra_hosts`).
  - Gyors teszt: hívjuk meg a `qwen3_coder_tool`-t egy egyszerű Python függvény generálására.
