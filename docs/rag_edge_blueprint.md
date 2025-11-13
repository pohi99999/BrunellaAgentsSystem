# RAG + Edge middleware blueprint

## RAG architektúra (Brunella dokumentáció)
1. **Források**: `PROJECT_OVERVIEW.md`, `docs/`, `README.dev.md`, `PROJECT_SUMMARY.md`.
2. **Pipeline**:
   - `langchain.text_splitter` (RecursiveCharacterSplitter, chunk 800/overlap 120).
   - Embedding modell: `text-embedding-004` (Gemini) vagy `qwen-embedding-v2`.
   - Tároló: `pgvector` (Cloud SQL) vagy `chroma` lokálisan.
3. **Lekérdezés**:
   - LangChain `RetrievalQA` → vertex AI / Gemini.
   - Kimenet JSON schema: `{"context": "...", "answer": "...", "sources": []}`.
4. **Üzemeltetés**:
   - Ingest job Cloud Run Cron (Scheduler) → Pub/Sub `rag-refresh`.
   - API végpont `/agent/rag-search` FastAPI routerben.

## Edge Functions + Next Middleware (pohanka.company frontendre)
1. **Edge Function** (Cloudflare Workers / Vercel Edge):
   - Feladata: JWT vagy session cookie ellenőrzése, IP rate limiting (kv kv store).
   - Forwardolja a kérelmet a Next.js API route felé.
2. **Next.js Middleware**:
   - `middleware.ts` figyeli a kritikus útvonalakat (`/dashboard`, `/api/secure/*`).
   - Ha hiányzik a `x-brunella-session` header vagy a felhasználó nincs whitelistben, redirect `/auth`.
3. **Observability**:
   - Edge log → Logflare/GA4.
   - Hibák Pub/Sub topicra (`edge-alerts`), amit a Brunella orchestrator olvas.
4. **Fejlesztői prompt minta**:
```
Feladat: készíts Next.js middleware-t, ami minden /dashboard alútvonal előtt:
1. Ellenőrzi a BRUNELLA_SESSION cookie-t.
2. Ha üres, 307 redirect /auth oldalra.
3. Ha van, írja ki a response headerbe az X-Session-Status: ok értéket.
```
