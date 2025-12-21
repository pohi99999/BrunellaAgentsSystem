# BrunellaAgentsSystem – projekt állapotjelentés (2025-12-21)

Ez a dokumentum a projekt **aktuális állapotát**, a **legutóbbi fejlesztések** összegzését, valamint a **következő lépésekre** vonatkozó javaslatokat rögzíti (különösen a stabil, demózható működéshez).

## 1) Rövid célkép
- A rendszer központi „OS” mintája: **Brunella (orchesztrátor)** → **specialista toolok/ügynökök**.
- Rövid táv: stabil, megbízható demó (tesztek + frontend build + E2E + Lighthouse), felhőben futó ellenőrzésekkel.
- Középtáv: bővíthető, multimodális képességek (kép/hang/szöveg), több modell/tool opció, vállalati testreszabás.

## 2) Jelenlegi architektúra (mi micsoda)
- **Backend**: FastAPI + LangGraph.
  - Belépési pont: `backend/src/app.py` (health endpoint + kódgenerálás endpoint).
  - Orchesztrátor graph: `backend/src/agent/graph.py`.
  - Toolok: `backend/src/agent/tools.py`.
  - Research specialist: `backend/src/specialists/research_agent/` (külön LangGraph).
  - Coder specialist: `backend/src/specialists/coder_agent.py`.
- **Frontend**: React + Vite + TypeScript.
  - Streaming kliens: `@langchain/langgraph-sdk/react`.

## 3) Modellek (aktuális működési elv)
- **Brunella / orchesztrátor**: Gemini 1.5 Pro (`gemini-1.5-pro-latest`) tool-callinggel.
- **Kódolás**: Qwen 3 Coder (DashScope) specialist toolon keresztül.
  - Ha a külső szolgáltatás nem elérhető, van **Ollama fallback** modell támogatás.
- **Kutatás**: Google Search grounding + Gemini használat.

## 4) Legutóbbi fejlesztések (lényeg)
- Backend stabilizálás:
  - Konténer indítás javítása (Uvicorn a valós appra mutat).
  - Importok egységesítése `src.*` névtér alatt.
  - „Lazy init” a kulcsok/LLM kliens létrehozásnál, hogy tesztek ne bukjanak import-időben.
- Compose egyszerűsítés:
  - A demó fókusz miatt kivezetésre kerültek a db/redis szolgáltatások a compose-ból.
- Frontend demó UX:
  - Új jobb oldali **Agent Graph** panel (vizuális monitoring + quick demo gombok), integrálva a chat nézetbe.
- Dokumentáció és biztonság:
  - A repóból eltávolításra kerültek a véletlenül dokumentált valódi API-kulcsok; `.env.example` csak placeholder.
  - README kapott egy rövid „Befektetői demó (gyors runbook)” részt.

Részletes munkajegyzet: `docs/SESSION_NOTES_2025-12-21.hu.md`

## 5) Validáció (mi futott le biztosan)
- **Backend tesztek**: zöld (pytest: 32 passed).
- **Frontend build/lint/E2E/Lighthouse**: GitHub Actions-ben futtatható stabilan (Node 20 runneren), a Codespaces környezetben lokálisan nem mindig ellenőrizhető.

## 6) Stabilitás: “felhőben fusson, ne a gépeden”
- A repóban van GitHub Actions CI: `.github/workflows/ci.yml`.
- Ez képes:
  - backend lint + tesztek,
  - frontend lint + build,
  - Playwright E2E,
  - Lighthouse audit.
- Javasolt workflow:
  1. Változtatás → commit
  2. GitHub Actions **CI** futtatás (Actions → CI → Run workflow)
  3. Csak akkor demózzunk / telepítsünk, ha a CI zöld.

## 7) Kritikus biztonsági megjegyzés
- Mivel a repóban korábban szerepeltek kulcsok, kezeld őket kompromittáltnak és **rotáld/tiltsd** (Gemini/DashScope/LangSmith). Akkor is, ha “dev” jellegűek voltak.

## 8) Javasolt következő lépések (prioritás)
1. **CI legyen a kapu**: minden fontos változtatás után fusson a teljes CI (backend + frontend + E2E + Lighthouse).
2. **Élő demó URL** (ha kell holnapra): CI zöld után deploy (pl. Cloud Run) – backend + frontend külön service.
3. **Gemma mint (A) lokális/fallback tool**:
   - Ne az orkesztrátor helyére, hanem külön specialist toolként (pl. summarizer/rewriter/classifier).
   - Egyszerű, izolált hibakezelés; kisebb kockázat.
4. **Megfigyelhetőség**: tool-hívások és hibák jól látható logokkal/tracinggel.
5. **Model “registry” / config**: 1 helyen legyen beállítva, melyik modell mire való (orchestrator/coder/research/fallback).

## 9) Fogalmi tisztázás (gyors)
- **Copilot**: fejlesztői IDE asszisztens (nem backend runtime modell).
- **Codex**: backendből hívható modell (API), külön specialistként érdemes integrálni.

---

Utolsó frissítés: 2025-12-21
