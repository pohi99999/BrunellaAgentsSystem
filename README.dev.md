# Brunella Agent System – Fejlesztői kézikönyv

## Befektetői demó (gyors runbook)

1. Hozz létre egy `.env` fájlt a gyökérben a `.env.example` alapján (a kulcsokat saját értékekre cserélve).
2. Indítás: `docker compose --env-file .env up -d --build`
3. Ellenőrzés:
  - Backend: `curl http://localhost:8000/health` → `{"status":"ok"}`
  - Frontend: http://localhost:3000

Részletesebb jegyzet és következő lépések: `docs/SESSION_NOTES_2025-12-21.hu.md`.

## Gyors indítás

1. Klónozd a repót és készíts `.env` fájlt a gyökérben: `copy .env.example .env`, majd töltsd ki a kulcsokat (GEMINI, QWEN, LANGSMITH).
2. Indítsd a teljes stack-et Windowsról: `run-stack.bat`. Ez automatikusan BuildKit-tel építi a képeket és futtatja a `docker compose --env-file .env up -d` parancsot (ugyanezt a parancsot kézzel is futtathatod bármely platformon).
3. Backend ellenőrzés: `curl http://localhost:8000/health` → `{"status":"ok"}`. Frontend: http://localhost:3000.

## Környezeti változók

| Kulcs               | Jelentés                                                                                   |
| ------------------- | ------------------------------------------------------------------------------------------ |
| `GEMINI_API_KEY`    | Google Gemini 1.5 Pro a fő orchestratorhoz (lokálisan közvetlen env-ből olvasva).          |
| `QWEN_API_KEY`      | DashScope kulcs a Qwen 3 Coder API-hoz.                                                    |
| `QWEN_CODER_MODEL`  | Alapértelmezett: `qwen-coder-plus-latest`.                                                 |
| `QWEN_API_BASE`     | OpenAI kompatibilis végpont, default: `https://dashscope.aliyuncs.com/compatible-mode/v1`. |
| `LANGSMITH_API_KEY` | Telemetria / LangSmith dashboard.                                                          |
| `OLLAMA_MODEL`      | Lokális fallback modell (pl. `qwen3:7b`).                                                  |
| `ENVIRONMENT`       | `development` (alapértelmezett) vagy `production` – utóbbinál a kulcsot Secret Managerből olvassuk. |
| `GCP_PROJECT_ID`    | Secret Manager projekt azonosítója; kötelező, ha `ENVIRONMENT=production`.                 |

A gyökérben lévő `.env` fájlt a `Makefile` automatikusan betölti, ezért a `make dev-*` parancsok is ugyanazokat a kulcsokat használják, mint a Docker Compose stack.

### Megjegyzés a titkokról

- A repó nem tartalmazhat valódi API-kulcsokat.
- Fejlesztéshez a `.env.example` csak placeholder értékeket ad; a tényleges kulcsokat `.env`-be (lokálisan) vagy Secret Manager/GitHub Secrets-be tedd.

## Hasznos parancsok

| Cél                   | Parancs                                     |
| --------------------- | ------------------------------------------- |
| Backend fejlesztés    | `make dev-backend` (LangGraph dev server)   |
| Frontend fejlesztés   | `make dev-frontend` (Vite)                  |
| Teljes dev mód        | `make dev`                                  |
| Docker stack állítása | `run-stack.bat` vagy `docker compose --env-file .env up -d` |
| Backend tesztek       | `cd backend && pytest`                      |
| Frontend lint         | `cd frontend && npm run lint`               |
| E2E tesztek           | `npm run test:e2e` (Playwright)             |
| Lighthouse audit      | `npm run build && npm run audit:ux`         |

## Qwen 3 Coder integráció

- A `backend/src/specialists/coder_agent.py` először a DashScope API-t hívja (`QWEN_API_KEY` szükséges).
- Ha nincs kulcs vagy a hívás hibára fut, automatikusan visszaesik az Ollama szolgáltatásra (`OLLAMA_MODEL`).
- A `docker-compose.yml` exportálja a szükséges változókat, Cloud Run esetén a `cloudbuild.yaml` injektálja a Secret Manager-ből.

## CI / CD

- GitHub Actions (`.github/workflows/ci.yml`): backend lint + pytest, frontend lint + build + Playwright + Lighthouse.
- Cloud Build (`cloudbuild.yaml`): tesztel, épít, Artifact Registry-be pushol, majd Cloud Run deploymentet futtat (backend + frontend) a megadott projektekben.

## Felhős futtatás – röviden

- A részletes Cloud Run útmutató itt érhető el: [`docs/cloud-run-deployment.hu.md`](docs/cloud-run-deployment.hu.md).
- Javasolt felállás: helyi fejlesztés Docker Compose-szal, éles futtatás két Cloud Run szolgáltatáson (backend + frontend).
- A GitHub → Cloud Build trigger minden `main` branch push után:
  1.  lefuttatja a backend teszteket (`pytest`) és a frontend lint + build lépéseket;
  2.  elkészíti és feltolja a konténerképeket az Artifact Registry-be;
  3.  telepíti a friss képeket Cloud Runra, a titkokat Secret Managerből olvasva.
- A szükséges környezeti változók (GEMINI, QWEN, LANGSMITH) Secret Manager titkokként kerülnek felvételre, így nem kell kézzel beírni őket a Cloud Run konzolban.

## Lighthouse & UX

- Konfiguráció: `frontend/lhci.config.js`.
- Kimenet: `.lighthouse/` mappába kerül, automatikus küszöbökkel (Performance ≥ 0.75, Accessibility ≥ 0.9).
- Playwright konfiguráció: `frontend/playwright.config.ts`, tesztek: `frontend/tests/e2e`.

## Hibakeresés

1. **Backend nem indul** – ellenőrizd a `.env`-et (különösen `GEMINI_API_KEY`) és nézd meg a backend konténer logját.
2. **Qwen hívás hibát ad** – futtasd `echo %QWEN_API_KEY%` Windows parancssorban vagy `printenv` Linuxon, illetve ellenőrizd a DashScope számlát.
3. **Playwright teszt lefagy** – `npx playwright install --with-deps` futtatása után ismételd meg.
4. **Lighthouse hiba** – töröld a `.lighthouse` mappát, futtasd újra a `npm run build && npm run audit:ux` parancsot, majd nézd át a `docs/ux_checklist.md` pontjait.

## DevOps tisztító ügynök futtatása

A `devops_agent.py` segédprogram minden nap 03:00-kor lefuttatja a `docker system prune -a -f --volumes` parancsot, és naplózza a
felszabadított tárhelyet. A script önállóan futtatható Pythonból:

```bash
pip install schedule
python devops_agent.py
```

### Példa systemd service

1. Másold a repót egy hosszú távon futó hostra.
2. Hozd létre a `/etc/systemd/system/devops-agent.service` fájlt:

```
[Unit]
Description=Brunella DevOps cleanup agent
After=docker.service

[Service]
WorkingDirectory=/opt/BrunellaAgentsSystem
ExecStart=/usr/bin/python3 /opt/BrunellaAgentsSystem/devops_agent.py
Restart=always

[Install]
WantedBy=multi-user.target
```

3. `sudo systemctl daemon-reload && sudo systemctl enable --now devops-agent`.

### Cron futtatás

Alternatíva, ha nem szeretnél service-t létrehozni: `crontab -e`, majd add hozzá:

```
@reboot cd /opt/BrunellaAgentsSystem && /usr/bin/python3 devops_agent.py >> devops_agent.log 2>&1
```

A script saját `while True` ciklusa miatt a cron bejegyzés egyszer indul el boot után, és folyamatosan életben tartja az ügynököt.

### Háttér konténer

Docker Compose vagy Kubernetes környezetben futtathatsz egy minimalista konténert is:

```yaml
services:
  devops-agent:
    build: .
    command: ["python", "devops_agent.py"]
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - ./:/app
    restart: unless-stopped
```

Ezzel a módszerrel az ügynök ugyanúgy eléri a host Docker daemonját (`docker.sock`), és gondoskodik a napi karbantartásról.
