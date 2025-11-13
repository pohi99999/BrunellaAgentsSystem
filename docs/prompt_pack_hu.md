# Magyar prompt/utasítás csomag – Brunella & webfejlesztés

Az alábbi sablonok a Gemini CLI-ben, GitHub Copilotban vagy bármely LLM-ben használhatók. Mindegyik blokk önállóan bemásolható.

## 1. Brunella backend – Qwen 3 Coder integráció
```
Feladat: Ellenőrizd, hogy a Brunella backend Qwen 3 Coder API-val kommunikál.
Lépések:
1. Nyisd meg a backend/src/specialists/coder_agent.py fájlt.
2. Ha van QWEN_API_KEY a környezetben, a DashScope (OpenAI kompatibilis) klienssel küldj kérést.
3. Hiba esetén térj vissza egyetlen soros "# HIBA: ..." üzenettel.
4. Ha nincs API kulcs, esel vissza az OLLAMA modellre (qwen3:7b).
5. Futtasd a pytest + mypy ellenőrzést.
```

## 2. Dev stack gyors indítása
```
Feladat: biztosítsd, hogy a fejlesztő egy parancsból elindíthassa a teljes stack-et.
Lépések:
1. Ellenőrizd, hogy létezik-e .env – ha nem, másold a .env.example-t.
2. DOCKER_BUILDKIT=1 változóval buildeld újra a képeket (powershell .\build-images.ps1).
3. Futtasd a docker compose up -d parancsot, majd ellenőrizd a http://localhost:8000/health végpontot.
4. Jelezd, ha hiányzik a GEMINI vagy QWEN kulcs.
```

## 3. Frontend UX audit
```
Feladat: futtasd a Lighthouse + Playwright ellenőrzéseket a frontend mappában.
Parancsok:
npm run lint
npm run test:e2e
npm run build && npm run audit:ux
Siker esetén töltsd fel a .lighthouse mappát artifactként vagy csatolj összefoglalót.
```

## 4. Dokumentáció frissítése
```
Feladat: írd át a README.dev.md összefoglalót a legutóbbi változtatások alapján.
1. Rövid bevezető (mit építünk).
2. Környezeti változók (.env.example).
3. Fejlesztői parancsok (make dev, run-stack.bat, npm run audit:ux).
4. Tesztelés (pytest, Playwright, Lighthouse).
5. Deploy folyamat (Cloud Build + Cloud Run).
```

## 5. RAG / Edge funkciók bővítése
```
Feladat: tervezz RAG-alapú keresőt Brunella dokumentációhoz.
Input: docs/, PROJECT_OVERVIEW.md
Output: rövid architektúra (embedding pipeline, vector store, kereső endpoint), Next.js Edge middleware koncepció a gyors jogosultság-ellenőrzéshez.
```
