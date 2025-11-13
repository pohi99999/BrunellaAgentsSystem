# AI-alapú „dev OS” megvalósítási útmutató

Ez a dokumentum a Brunella Agent System (BAS) köré épített, AI-vezérelt fejlesztői környezet implementációs tervének technikai levezényléséhez készült. A cél egy olyan workflow, amely a lokális fejlesztéstől a felhőbeli üzemeltetésig (DevOps + MLOps) konzisztens és nagy arányban automatizált folyamatokat biztosít.

## 1. Kiindulási állapot – gyors audit

- **Konténer stack**: `docker-compose.yml` teljes (backend, frontend, Postgres, Redis). A `run-stack.bat` + `build-images.ps1` szkriptek kényelmes lokális indítást adnak.
- **Backend**: FastAPI + LangGraph (Python 3.11). A frissített `backend/Dockerfile` az egész `src/` tartalmat beemeli a buildbe, így a pip install réteg determinisztikus.
- **Frontend**: React/Vite + Tailwind. Dockerfile multi-stage buildet használ nginx-szel.
- **DevContainer**: VS Code + Docker outside of Docker + Python/PowerShell toolchain, Copilot beköthető.
- **CI/CD hiányosságok**: Nem volt GitHub Actions pipeline, Cloud Build definíció sem, így a korábbi koncepció csak terv szintjén élt.

## 2. Lokális fejlesztés & konténerizáció

1. **.env kezelés** – töltsd ki a következő kulcsokat a repo gyökerében (nem verziókezelve): `GEMINI_API_KEY`, `QWEN_API_KEY`, `LANGSMITH_API_KEY`, opcionálisan `OLLAMA_MODEL`.
2. **Docker image frissítés** – `build-images.ps1 -CacheDir ".buildx-cache"` vagy `docker compose build`. A backend Dockerfile most a forrásfájlokat korán másolja be, így a pip install hibatűrőbb.
3. **Lokális stack** – `run-stack.bat` futtatása vagy natívan `docker compose up -d`. Health-check: `curl http://localhost:8000/health`.
4. **Devcontainer** – `Dev Containers: Reopen in Container` VS Code-ból. A containeren belül `make -C backend test` ellenőrzi az ügynök logikát, `npm run dev` a frontendnek.

## 3. CI/CD automatizmusok

### 3.1 GitHub Actions

Új workflow: `.github/workflows/ci.yml`

- **Backend job**: Python 3.11, `pip install -r requirements.txt`, `ruff check`, `pytest`.
- **Frontend job**: Node 20, `npm ci`, `npm run lint`, `npm run build`.
- **Trigger**: push `main`/`develop`, minden PR.

### 3.2 Cloud Build pipeline

`cloudbuild.yaml` biztosítja a GCP oldali buildelést és deploy-t.

1. **Teszt lépések**: külön Python és Node konténerekben futó backend teszt és frontend build.
2. **Docker image építés**: backend + frontend image a `${_REGION}-docker.pkg.dev/${_PROJECT_ID}/${_ARTIFACT_REPO}` registry-be.
3. **Felhő deploy**: Cloud Run szolgáltatások (`_BACKEND_SERVICE`, `_FRONTEND_SERVICE`) frissítése. API kulcsok Secret Managerből kerülnek injektálásra a `--set-secrets` zászlóval.
4. **Szükséges manuális lépések**:
   - Artifact Registry repository (`${_ARTIFACT_REPO}`) létrehozása.
   - Cloud Build service account jogosultságok: `roles/run.admin`, `roles/artifactregistry.writer`, `roles/secretmanager.secretAccessor`.
   - Trigger konfigurálása (pl. `main` push, PR felülvizsgálat vagy manuális indítás).

## 4. Felhő infrastruktúra

| Blokk | Ajánlott szolgáltatás | Feladat |
| --- | --- | --- |
| **Runtime** | Cloud Run (backend + frontend) | Konténer image automatikus deploy Cloud Buildből. |
| **Adatbázis** | Cloud SQL Postgres + Memorystore Redis | A compose-ban használt szolgáltatásokat 1:1-ben váltsa ki, VPC Connectoron keresztül érhető el. |
| **Artifact storage** | Artifact Registry | A Cloud Build pipeline célja. |
| **Infra as Code** | Terraform / CDKTF | GCP projektek, Pub/Sub topicok, Scheduler jobok, secrets. A dev/staging/prod projektekre külön state. |

## 5. Üzenetközpont, időzítés, orchestrator

1. **Pub/Sub struktúra**:
   - `task-request`, `task-result`, `alerts`, `maintenance`.
   - A BAS backend kezdetben REST-en szolgál ki, de később Cloud Functions/Run subscriber szolgáltatásként hallgathatja a topicokat.
2. **Cloud Scheduler + Functions**:
   - `maintenance-prune` (Docker/image cleanup).
   - `daily-backup` (DB snapshot + Drive feltöltés).
   - `model-retrain` (Vertex AI Pipeline indító).
3. **Brunella orchestrator**:
   - GitHub webhook → Pub/Sub → BAS orchestrator.
   - Monitoring alert webhook → Pub/Sub `alerts`.
   - Workspace akciók (Calendar/Drive/Gmail) dedikált service accounttal, domain-wide delegationnel.

## 6. MLOps & Vertex AI

1. **Model registry**: Vertex AI Model Registry-ben tárold a BAS által használt finomhangolt modelleket.
2. **Pipeline**: Vertex AI Pipelines (Kubeflow DSL vagy TFX) – adat előkészítés, tréning, validáció, endpoint frissítés.
3. **Trigger**: Cloud Build (ML repo változás) vagy Cloud Scheduler (időzített re-train) -> Cloud Workflows -> Vertex Pipeline run.
4. **Monitoring**: Vertex AI Model Monitoring (drift/alert) → Pub/Sub `alerts` → BAS orchestrator.

## 7. Workspace és értesítések

| Integráció | Technikai megjegyzés |
| --- | --- |
| Calendar | Cloud Functions + Calendar API, service account delegálással. Release/határidő események auto létrehozása. |
| Drive/Docs | Build/log riportok generálása és feltöltése; Cloud Functions használhatja a Drive API-t. |
| Gmail | Hibariadó vagy pipeline státusz e-mail. Secret Manager tárolja az OAuth hitelesítést. |
| Google Chat | ChatOps bot → Cloud Run service, amely a BAS orchestrator felé fordítja a parancsokat. |

## 8. Megfigyelés & biztonság

1. **Cloud Monitoring**: egyedi dashboard a BAS latency, queue hossz, Build sikeresség mutatókkal. Alert Policy → Pub/Sub.
2. **Log feldolgozás**: Cloud Logging sink → BigQuery / Storage az elemzéshez.
3. **IAM**: project szintenként külön service account, legkisebb jogosultság elv. IAP vagy JWT alapú védelem a Cloud Run backendhez (ha nem publikus).
4. **Secret kezelés**: minden API kulcs Secret Managerben, GitHub Actions oldalán GitHub Secrets; Cloud Build `--set-secrets` már fel van vezetve.
5. **Supply chain**: Artifact Registry vulnerability scanning, Dependabot/GHAS riasztások, Cloud Build attesztáció (Binary Authorization ha szükséges).

## 9. Fokozatos bevezetés – javasolt ütemezés

| Sprint | Fő fókusz | Kulcs deliverable |
| --- | --- | --- |
| S1 | Lokális stabilizálás | Docker stack → ok, DevContainer csapat-szintű dokumentálása. |
| S2 | CI/CD + Artifact Registry | GitHub Actions + Cloud Build trigger, első felhős deploy dev projektbe. |
| S3 | Pub/Sub + Scheduler | Karbantartó funkciók, alap alerting csatorna. |
| S4 | Workspace + ChatOps | Calendar/Gmail automatizmusok, első Chat bot prototípus. |
| S5 | Vertex AI pipeline | Modell tréning + monitoring, orchestrator bővítés. |
| Folyamatos | Biztonsági audit + költségfigyelés | IAM review, Cloud Monitoring tuning, finomhangolt auto-scaling. |

## 10. Függőségek & következő teendők

1. **GCP előkészítés**: projektek (dev/staging/prod), billing, API enable. Cloud Build SA jogosultságok kiosztása.
2. **Secretek feltöltése**: GEMINI, QWEN, LANGSMITH, Firebase, Gmail, Jira – Secret Manager + GitHub Secrets.
3. **Networking döntés**: szükség van-e privát Cloud Run-ra → IAP + VPC Connector, vagy marad publikus endpoint Auth headerrel.
4. **BAS orchestrator fejlesztés**: GitHub webhook feldolgozó, Pub/Sub listener, CrewAI/LangGraph integráció, auto-javítás guardrail szabályok.
5. **Dokumentáció**: tartalom jelen fájl + `PROJECT_OVERVIEW.md` hivatkozás; csapat onboarding wiki frissítése.

Ezeknek a lépéseknek a végrehajtásával a Brunella Agent System fokozatosan elmozdul a teljesen automatizált, AI-vezérelt „dev OS” működés felé. Minden blokk külön-külön aktiválható, így a csapat kontrolláltan, mérhető eredmények mellett tudja bevezetni az új képességeket.
