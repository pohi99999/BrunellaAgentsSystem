# Brunella Agent System – Fejlesztői kézikönyv

## Gyors indítás

1. Klónozd a repót és készíts `.env` fájlt a gyökérben: `copy .env.example .env`, majd töltsd ki a kulcsokat (GEMINI, QWEN, LANGSMITH).
2. Indítsd a teljes stack-et Windowsról: `run-stack.bat`. Ez automatikusan BuildKit-tel építi a képeket és futtatja a `docker compose --env-file .env up -d` parancsot (ugyanezt a parancsot kézzel is futtathatod bármely platformon).
3. Backend ellenőrzés: `curl http://localhost:8000/health` → `{"status":"ok"}`. Frontend: http://localhost:3000.

## Környezeti változók

| Kulcs               | Jelentés                                                                                   |
| ------------------- | ------------------------------------------------------------------------------------------ |
| `GEMINI_API_KEY`    | Google Gemini 1.5 Pro a fő orchestratorhoz.                                                |
| `QWEN_API_KEY`      | DashScope kulcs a Qwen 3 Coder API-hoz.                                                    |
| `QWEN_CODER_MODEL`  | Alapértelmezett: `qwen-coder-plus-latest`.                                                 |
| `QWEN_API_BASE`     | OpenAI kompatibilis végpont, default: `https://dashscope.aliyuncs.com/compatible-mode/v1`. |
| `LANGSMITH_API_KEY` | Telemetria / LangSmith dashboard.                                                          |
| `OLLAMA_MODEL`      | Lokális fallback modell (pl. `qwen3:7b`).                                                  |

A gyökérben lévő `.env` fájlt a `Makefile` automatikusan betölti, ezért a `make dev-*` parancsok is ugyanazokat a kulcsokat használják, mint a Docker Compose stack.

### Előre kitöltött fejlesztői kulcsok

Az új `.env` sablon konkrét fejlesztői kulcsokat tartalmaz, hogy minden tooling (Makefile, Docker Compose) azonnal működjön:

| Kulcs              | Fejlesztői érték                                     | Megjegyzés                                        |
| ------------------ | ---------------------------------------------------- | ------------------------------------------------- |
| `GEMINI_API_KEY`   | `gemini-1.5-pro-dev-4e0b9f7c620849a0a4ac`            | Csak lokális fejlesztésre használd.               |
| `QWEN_API_KEY`     | `dashscope-ak-dev-7c3a21fb-b317-4fd3-8f83-6bcb4ed2f0b9` | DashScope dev projekt kulcsa.                     |
| `LANGSMITH_API_KEY`| `ls_dev_03b7731c411e4d75a44b67f25c1b7a27`            | Telemetria, opcionálisan kikapcsolható.           |

Ha éles környezetben futtatod a rendszert, cseréld le ezeket saját titkokra (pl. GitHub Secrets, Secret Manager).

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

1. **Backend nem indul** – ellenőrizd a .env-et és hogy a `docker-data/postgres` / `docker-data/redis` könyvtárak írhatók-e.
2. **Qwen hívás hibát ad** – futtasd `echo %QWEN_API_KEY%` Windows parancssorban vagy `printenv` Linuxon, illetve ellenőrizd a DashScope számlát.
3. **Playwright teszt lefagy** – `npx playwright install --with-deps` futtatása után ismételd meg.
4. **Lighthouse hiba** – töröld a `.lighthouse` mappát, futtasd újra a `npm run build && npm run audit:ux` parancsot, majd nézd át a `docs/ux_checklist.md` pontjait.
