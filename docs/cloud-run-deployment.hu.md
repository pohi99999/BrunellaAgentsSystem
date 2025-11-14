# Brunella Agent System – Cloud Run telepítési útmutató

Ez a dokumentum lépésről lépésre bemutatja, hogyan állíthatod be a Brunella Agent Systemet úgy, hogy a fejlesztést továbbra is a helyi gépeden végezd Docker Compose-szal, miközben a GitHub-ba tolt módosításokat a Google Cloud automatikusan építi és két Cloud Run szolgáltatásra (backend + frontend) telepíti. A folyamat költséghatékony, kezdésnek is ideális.

> **Ajánlott felállás**
>
> - Helyi fejlesztés: `docker compose` + Postgres/Redis konténerek (ingyenes).
> - Felhő: Artifact Registry + Cloud Build + Cloud Run (backend, frontend). Titkok kezelése: Secret Manager.
> - Adatbázis/Redis: kezdetben maradjon a helyi gépen; később válthatsz Cloud SQL + Memorystore párosra.

---

## 1. Előfeltételek

1. Google Cloud projekted, **Billing** engedélyezve.
2. Telepített és bejelentkezett [`gcloud` CLI](https://cloud.google.com/sdk/docs/install) (verzió ≥ 445.0.0).
3. GitHub repó összekötve a Google Cloud Console-lal (Cloud Build GitHub App, lásd 5. fejezet).
4. A repó gyökerében található `.env.example` alapján kitöltött `.env` (lokális futtatáshoz).

```text
# Állítsd be a CLI-ben az alap projektet és régiót (példa)
gcloud config set project <PROJECT_ID>
gcloud config set builds/use_kaniko True
```

_Ajánlott régió:_ `europe-west1` (Frankfurt) – jól illeszkedik a `cloudbuild.yaml` alapértelmezéseihez.

---

## 2. Lokális fejlesztési rutin (összefoglaló)

1. `.env` létrehozása: `copy .env.example .env` (Windows) vagy `cp .env.example .env` (Linux/macOS).
2. Kulcsok kitöltése: `GEMINI_API_KEY`, `QWEN_API_KEY`, `LANGSMITH_API_KEY` (opcionális).
3. Stack indítása: `run-stack.bat` (Windows) vagy `docker compose up -d`.
4. Tesztek, lintelés:
   - Backend: `cd backend && pytest`
   - Frontend: `cd frontend && npm run lint`
   - E2E: `npm run test:e2e`

Ha ezek zöldek, mehet a commit + push a `main` (vagy kiválasztott) branch-re, ami a Cloud Build triggert indítja.

---

## 3. Artifact Registry beállítása

1. Engedélyezd az Artifact Registry API-t:
   ```text
   gcloud services enable artifactregistry.googleapis.com
   ```
2. Hozz létre egy Docker repository-t (pl. `brunella` néven):
   ```text
   gcloud artifacts repositories create brunella \
     --repository-format=docker \
     --location=europe-west1 \
     --description="Brunella Agent artifactok"
   ```
3. Jegyezd fel a később használt URI-t: `europe-west1-docker.pkg.dev/<PROJECT_ID>/brunella`.

---

## 4. Secret Manager

1. Engedélyezd a Secret Manager szolgáltatást:
   ```text
   gcloud services enable secretmanager.googleapis.com
   ```
2. Hozd létre a szükséges titkokat (első verzió feltöltéssel):
   ```text
   echo -n "<GEMINI_API_KEY>" | gcloud secrets create GEMINI_API_KEY --data-file=-
   echo -n "<QWEN_API_KEY>" | gcloud secrets create QWEN_API_KEY --data-file=-
   echo -n "<LANGSMITH_API_KEY>" | gcloud secrets create LANGSMITH_API_KEY --data-file=-
   ```
   > Ha később frissítenéd a kulcsokat: `gcloud secrets versions add GEMINI_API_KEY --data-file=-`.
3. Adj hozzáférést a Cloud Build és Cloud Run service accountoknak (lásd 6. fejezet).

---

## 5. Cloud Run szolgáltatások létrehozása

> A telepítés maga a Cloud Build pipeline-ból történik, de a szolgáltatások első verzióját célszerű előkészíteni (helykitöltő image-del), így a titkok és CPU/memória beállítások is rögzíthetők.

1. Engedélyezd a szükséges API-kat:
   ```text
   gcloud services enable run.googleapis.com compute.googleapis.com cloudbuild.googleapis.com
   ```
2. Backend szolgáltatás (ideiglenes image-szel):
   ```text
   gcloud run deploy brunella-backend \
     --image=gcr.io/cloudrun/hello \
     --region=europe-west1 \
     --allow-unauthenticated
   ```
3. Frontend szolgáltatás hasonlóan:
   ```text
   gcloud run deploy brunella-frontend \
     --image=gcr.io/cloudrun/hello \
     --region=europe-west1 \
     --allow-unauthenticated
   ```
4. A későbbi deploy parancsok (`cloudbuild.yaml`) felülírják az image-ket és beállítják a titkokat.

**Ajánlott konfigurációk**

- CPU: 1, memória: 1 GiB (backend), 512 MiB (frontend) – igény szerint később növelhető.
- Konkurencia: 10–20 (backend), 80 (frontend).

---

## 6. Jogosultságok és service accountok

### 6.1 Cloud Build service account

A Cloud Build alapértelmezett service account: `PROJECT_NUMBER@cloudbuild.gserviceaccount.com`. Adj neki jogosultságot, hogy:

- képeket pusholhasson az Artifact Registry-be,
- titkokat olvashasson a Secret Managerből,
- Cloud Run szolgáltatást telepíthessen.

```text
gcloud projects add-iam-policy-binding <PROJECT_ID> \
  --member="serviceAccount:<PROJECT_NUMBER>@cloudbuild.gserviceaccount.com" \
  --role="roles/artifactregistry.writer"

gcloud projects add-iam-policy-binding <PROJECT_ID> \
  --member="serviceAccount:<PROJECT_NUMBER>@cloudbuild.gserviceaccount.com" \
  --role="roles/run.admin"

gcloud projects add-iam-policy-binding <PROJECT_ID> \
  --member="serviceAccount:<PROJECT_NUMBER>@cloudbuild.gserviceaccount.com" \
  --role="roles/iam.serviceAccountUser"

gcloud secrets add-iam-policy-binding GEMINI_API_KEY \
  --member="serviceAccount:<PROJECT_NUMBER>@cloudbuild.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
# Ismételd meg QWEN_API_KEY és LANGSMITH_API_KEY titkokra is.
```

### 6.2 Cloud Run runtime service account (opcionális)

Ha külön service accounttal futtatnád a backend/frontendet (pl. későbbi GCP erőforrás eléréshez), hozd létre és add meg a `--service-account` flaget a `cloudbuild.yaml` deploy lépéseiben.

---

## 7. Cloud Build trigger GitHubra

1. Cloud Console → Cloud Build → Triggerek → "Create Trigger".
2. Válaszd a **GitHub (Cloud Build GitHub App)** opciót, kössed össze a repót.
3. Trigger konfiguráció:
   - Név: `brunella-main`
   - Esemény: `Push`
   - Branch: `^main$`
   - Konfiguráció: `cloudbuild.yaml`
   - Substitutions (ha eltérnek az alapértelmezések):
     - `_PROJECT_ID`, `_REGION`, `_ARTIFACT_REPO`, `_BACKEND_SERVICE`, `_FRONTEND_SERVICE`, `_PUBLIC_API_BASE`
4. Mentsd el. Teszteld egy próba commit push-sal.

Az első build ~8–12 perc lehet (Docker layer cache nélkül). A későbbiek gyorsabbak.

---

## 8. `cloudbuild.yaml` áttekintése

A gyökérben lévő `cloudbuild.yaml` már tartalmazza a szükséges lépéseket:

1. Backend tesztek (`pytest`) futtatása.
2. Frontend lint + build.
3. Képek építése Kanikó helyett Dockerrel (Cloud Build szerverless környezete). A build context `backend/` és `frontend/`.
4. Képek pusholása az Artifact Registry-be.
5. Cloud Run deploy backend + frontend:
   - Titkok: `GEMINI_API_KEY`, `QWEN_API_KEY`, `LANGSMITH_API_KEY` Secret Managerből.
   - Extra env: `QWEN_CODER_MODEL`, `QWEN_API_BASE` (szükség szerint módosítható substitutions-szel).

**Tipp:** ha staging környezetet szeretnél később, duplázd meg a deploy lépést másik szolgáltatásnévvel és substitution-nel.

---

## 9. Első telepítés ellenőrzése

1. Push egy commitot a `main` branch-re.
2. Cloud Console → Cloud Build → Build history: ellenőrizd, hogy sikeres-e a pipeline.
3. Cloud Run → Services → `brunella-frontend`: nyisd meg a URL-t. A frontenden állítsd be az API végpontot (`VITE_API_URL`) a substitutions-ben.
4. Backend URL: `brunella-backend` Cloud Run szolgáltatás URL-je, pl. `https://<hash>-uw.a.run.app/agent`.
5. Teszteld: `curl <BACKEND_URL>/health`.

---

## 10. Költségfigyelés

- Cloud Run: free tier havi ~2 millió kérést tartalmaz; tartósan futó szolgáltatásnál néhány euró/hó.
- Artifact Registry tárhely: első 0.5 GiB ingyen, utána kb. 0.10 €/GiB/hó.
- Cloud Build: 120 build perc/hó ingyen; utána ~0.0034 €/perc.
- Secret Manager: első 6 titok ingyen, utána 0.06 €/titok/hó.

A fejlesztői workflow így nagyon alacsony költséggel üzemeltethető. Figyeld a Billing → Budgets & Alerts felületen a kiadásokat.

---

## 11. Következő lépések

- **Cloud SQL + Memorystore**: ha éles adatokkal dolgozol, válts menedzselt adatbázisra. A backend `DATABASE_URL` és `REDIS_URL` értékeit a Cloud Run környezeti változói között állítsd be.
- **Staging környezet**: hozz létre második Artifact Registry / Cloud Run szolgáltatást (pl. `brunella-backend-staging`), és készíts külön build triggert.
- **Megfigyelhetőség**: aktiváld a Cloud Logging + Error Reporting integrációkat; a `LANGSMITH_API_KEY` segít az agent flow-k vizualizálásában.
- **Automatikus tesztek**: bővítsd a `cloudbuild.yaml`-t Playwright futtatással (Dockerized környezetben), ha frontendes regressziókat is szeretnél elkapni.

---

## 12. Gyors ellenőrző lista telepítés előtt

- [ ] `.env` kitöltve, lokális tesztek futnak.
- [ ] Artifact Registry repo létezik, Cloud Build SA rendelkezik `artifactregistry.writer` jogosultsággal.
- [ ] Secret Manager titkok feltöltve, Cloud Build SA olvasási jogosultsággal.
- [ ] Cloud Run szolgáltatások létrehozva (`brunella-backend`, `brunella-frontend`).
- [ ] GitHub trigger aktív és a substitutions értékek helyesek.
- [ ] Első build lefutott, URL-ek elérhetőek (`curl /health`).

Kész is! Innentől minden `main` branch-re pusholt változtatás automatikusan buildeli és frissíti a Cloud Run szolgáltatásaidat, miközben te kényelmesen fejleszthetsz a saját gépeden Docker Compose-szal.
