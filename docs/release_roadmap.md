# Release Roadmap – Brunella Agent System (2025 Q4 – 2026 Q1)

## Milestone 1 – Dev stabilizáció (nov. 15.)
* Docker-compose stack és `.env` sablon „out-of-the-box” működik.
* Qwen 3 Coder API kulcsok Secret Managerben.
* GitHub Actions → lint + pytest + Playwright + Lighthouse.

## Milestone 2 – Felhőben futó orchestrator (nov. 30.)
* Cloud Build trigger a `main` ágra.
* Artifact Registry → Cloud Run deploy (backend + frontend).
* Pub/Sub topicok (task-request, alerts) és Cloud Scheduler maintenance job.

## Milestone 3 – Workspace + MLOps integráció (dec. 20.)
* Calendar / Drive / Gmail automatizmusok (service account).
* Vertex AI pipeline első futása, modell monitorozás bekötése.
* RAG-alapú tudásbázis Pohi dokumentációkra.

## Milestone 4 – Production hardening (jan. 31.)
* Edge security (IAP vagy JWT), rate limiting, audit logok.
* GA4 / Log Explorer dashboard, incidenskezelés.
* Release candidate, dokumentált rollback terv, Release Note sablon.
