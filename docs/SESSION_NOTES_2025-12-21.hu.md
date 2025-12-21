# Munkajegyzet – 2025-12-21 (befektetői demó stabilizálás)

## Cél
- A stack induljon megbízhatóan (Docker/Compose), és a demó „kinézetre” is vállalható legyen.
- Backend oldalon a tesztfutás ne bukjon el import-időben (kulcs/secret hiány miatt).
- Frontendben legyen egy látványos „Agent Graph” monitor panel.

## Végrehajtott változások (összefoglaló)

### Backend – megbízható indítás + csomagolás
- **Konténer belépési pont javítása**: a backend konténer indítása a valós FastAPI appra mutat.
  - Érintett: `backend/Dockerfile` (Uvicorn: `src.app:app`)
- **Importok egységesítése**: `src.*` névtér alatt következetes importálás.
  - Érintett: `backend/src/app.py`, `backend/src/agent/tools.py`, `backend/src/agent/graph.py`, `backend/src/specialists/research_agent/graph.py`

### Backend – „lazy init” a titkokhoz (tesztbarát)
- **Kliens/LLM létrehozás import-idő helyett futáskor**:
  - Research agent: a Google GenAI `Client` csak akkor jön létre, amikor a kutatás ténylegesen fut.
  - Orchestrator: a Gemini LLM lazy módon készül, és cache-elve van.
  - A tesztekhez vissza lett téve egy patch-elhető `llm` változó, hogy a meglévő tesztpatch-ek működjenek.
  - Érintett: `backend/src/specialists/research_agent/graph.py`, `backend/src/agent/graph.py`

### Docker Compose – demó egyszerűsítés
- **Komplexitás csökkentése**: a Compose-ból kikerült a Postgres + Redis (demó fókusz).
  - Érintett: `docker-compose.yml`

### Biztonság – titkok és env sablonok rendbetétele
- **Véletlenül dokumentált API-kulcsok eltávolítva** (a repóban csak placeholder maradhat).
  - Érintett: `README.dev.md`, `backend/.env.example`
- **`.env.example` összhang a Compose-szal** (db/redis kivezetve a demo compose miatt).
  - Érintett: `.env.example`

### Frontend – befektetői „Agent Graph” panel
- **Új jobb oldali panel**: egyszerű, látványos SVG-alapú “Agent Graph” megjelenítés, és 2 gyors demó gomb (kutatás + kódolás).
  - Érintett: `frontend/src/components/AgentGraphPanel.tsx` (új)
- **Integráció a chat layoutba**: nagy kijelzőn (lg+) jobb oldalt megjelenik a panel.
  - Érintett: `frontend/src/components/ChatMessagesView.tsx`
- **Szélesebb app layout**: hogy kényelmesen elférjen a panel.
  - Érintett: `frontend/src/App.tsx`

## Validáció / állapot
- **Backend tesztek**: `32 passed` (csak deprecations warningok).
- **Frontend build/lint**: ebben a környezetben nem volt validálható (Node/npm hiány vagy korlátozás miatt). Emiatt előfordulhat, hogy a TS/JSX hibák csak tooling hiányból látszanak, de ezt CI-vel vagy Node-os környezettel érdemes fixen ellenőrizni.

## Gyors demó run (javasolt)
- `docker compose --env-file .env up -d --build`
- Frontend: `http://localhost:3000`
- Backend health: `curl http://localhost:8000/health`

## Kockázatok / nyitott pontok
- **Frontend ellenőrizhetőség**: szükséges egy olyan környezet (devcontainer/CI), ahol van Node 20+ és futtatható `npm ci && npm run build`.
- **Agent Graph „indíthatóság”**: jelenleg a panel demó gombjai a chat submitot használják (vizuális + UX demó), de nincs külön backend API a „csomópont indítására”.
- **Tech debt jelzések**: Pydantic/LangGraph deprecations – nem sürgős a demóra, de érdemes később rendbe tenni.

## Javasolt következő lépések (prioritás szerint)
1. **Frontend build ellenőrzés CI-ben vagy Node-os devcontainerben**: `npm ci`, `npm run lint`, `npm run build`.
2. **Ha TS hibák ténylegesek**: az `AgentGraphPanel.tsx` importok/aliasok finomhangolása (pl. path alias konzisztencia), és minimális típusjavítás.
3. **Demó “agent indítás” minimal endpoint**: opcionálisan 1 egyszerű backend végpont (pl. `/demo/run-research`, `/demo/run-coder`), amit a panel gombjai hívnak.
4. **README/dev titkok átnézése**: ha van bárhol hardcode-olt “dev kulcs”, azt érdemes eltávolítani és csak `.env.example`-ben placeholderként tartani.
