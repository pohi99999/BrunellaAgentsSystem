# Brunella Agent System – összefoglaló (2025-11-13)

## Mit végeztünk el?

1. **Qwen 3 Coder integráció**  
   - A `backend/src/specialists/coder_agent.py` most először DashScope (OpenAI kompatibilis) API-n keresztül hívja a Qwen 3 Coder modellt (`QWEN_API_KEY`, `QWEN_CODER_MODEL`, `QWEN_API_BASE`).  
   - Ha nincs kulcs vagy hibázik a hívás, automatikusan visszaesik az Ollama `qwen3:7b` modellre.  
   - A konfigurációs fájlok (`config.yaml`, `docker-compose.yml`, `.env.example`) ehhez idomultak.

2. **Fejlesztői környezet gyorsítása**  
   - Új, tiszta `.env.example` készült a gyökérben; a `run-stack.bat` automatikusan másolatot készít, ha hiányzik `.env`.  
   - A Docker Compose környezeti változói rendezettek, az `OLLAMA_MODEL` default értéke is frissült.  
   - A fejlesztők így egy parancsból (run-stack + docker compose) fel tudják húzni a teljes stack-et.

3. **CI/CD bővítés**  
   - GitHub Actions workflow (`.github/workflows/ci.yml`) most backend lint+pytest mellett Playwright és Lighthouse futtatást is végrehajt a frontendre.  
   - A Cloud Build pipeline (`cloudbuild.yaml`) kezel minden Qwen-specifikus env-t és a Cloud Run deploy során Secret Managerből tölti be a kulcsokat.

4. **Frontend audit tooling**  
   - Playwright + LHCI konfigurációk (`frontend/playwright.config.ts`, `frontend/tests/e2e`, `frontend/lhci.config.js`, `package.json` scriptjei) kiépültek.  
   - Új `docs/ux_checklist.md` segíti a manuális ellenőrzéseket (hero animáció, navigáció, hozzáférhetőség).

5. **Dokumentációk és promptok**  
   - `README.dev.md` részletes fejlesztői kézikönyv, `ProjectManifest.json` formális metaadat, `docs/release_roadmap.md` a következő mérföldköveket írja le.  
   - `docs/prompt_pack_hu.md` magyar nyelvű promptcsomag Gemini CLI / Copilot használathoz.  
   - `docs/rag_edge_blueprint.md` RAG + Edge middleware terv.

## Hátralévő lépések (ajánlott sorrend)

1. **Környezeti változók kitöltése**  
   - Töltsd ki a `.env`-ben a `GEMINI_API_KEY`, `QWEN_API_KEY`, `LANGSMITH_API_KEY` mezőket (és Cloud Secret Managerben is).

2. **Lint hibák javítása (frontend)**  
   - `npm run lint` még `any` típusokra panaszkodik. Adj típusdefiníciókat az `App.tsx`, `ActivityTimeline`, `ChatMessagesView` fájlokban, hogy a CI zöld legyen.

3. **Playwright/Lighthouse futtatás**  
   - Telepítsd a Playwright böngészőket: `cd frontend && npx playwright install --with-deps`.  
   - Futtasd sorban: `npm run lint`, `npm run test:e2e`, `npm run build && npm run audit:ux`. Vizsgáld meg a `.lighthouse` riportot.

4. **Cloud Build paraméterezése**  
   - Állítsd be a valós `_PROJECT_ID`, `_REGION`, `_PUBLIC_API_BASE` értékeket.  
   - Hozd létre az Artifact Registry-t és a Cloud Run szolgáltatásokat, majd engedélyezd a trigger(eke)t.

5. **Pub/Sub + Scheduler bekötés**  
   - Hozd létre a `task-request`, `alerts`, `maintenance` topikokat és a kapcsolódó Cloud Scheduler jobokat (pl. docker prune, backup, model retrain).  
   - Drótozd be ezeket a Brunella orchestratorhoz (FastAPI endpoint + Pub/Sub listener).

6. **Workspace + MLOps integráció**  
   - Service account Calendar/Drive/Gmail hozzáféréssel; készítsd elő a Vertex AI pipeline első futását (adat → tréning → deploy).  
   - A `docs/release_roadmap.md` Milestone 3 tartalmazza a részleteket.

7. **Webes UX finomítás**  
   - Tisztázd a Whisk/partikula animációk részleteit, kísérletezz GSAP/Three.js effektekkel, és ellenőrizd mobilon is a teljesítményt.  
   - Készítsd el az interaktív kártyák neon-szegély és tilt animációját.

Az itt leírtak alapján a csapat és a ChatGPT/Gemini asszisztens is átlátja, mi történt, és pontosan milyen következő lépésekkel jutunk el a következő release szintre. Jó munkát a folytatáshoz! 🎯
