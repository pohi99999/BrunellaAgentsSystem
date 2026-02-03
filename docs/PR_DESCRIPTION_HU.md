# Biztonsági, tesztelési és infrastrukturális fejlesztések az AGENT.md alapján

Az AGENT.md-ben meghatározott mind a 8 fejlesztési feladat megvalósítása: sebességkorlátozás, prompt injekció védelem, kutatási ügynök integrációs tesztek, függőség rögzítés, központosított naplózás és architektúra dokumentáció.

## Biztonsági Megerősítés

**Sebességkorlátozás** - `slowapi` hozzáadása 10 kérés/perc korláttal a `/coder/generate` végponton IP címenként. 429-es válaszkódot ad vissza korlát túllépésekor.

**Prompt Injekció Védelem** - Validátor létrehozása 14 regex mintával, amely blokkolja a rendszer felülírásokat, script injekciót és szerepmanipulációt:

```python
# A CodeRequest validációban
@field_validator("prompt")
def validate_prompt_field(cls, v: str) -> str:
    return validate_prompt(v)  # ValueError-t dob blokkolt minták esetén
```

Blokkolt minták többek között: `ignore (previous|all) instructions`, `system:`, `<script>`, `pretend you are`, stb. Minden blokkolás WARNING szinten naplózva.

## Tesztelés

**Kutatási Ügynök Integrációs Tesztek** - Teljes gráf ciklus tesztek mock GenAI klienssel. Validálja az állapot átmeneteket, maximális ciklus érvényesítést és AIMessage kimeneteket megfelelő OverallState típusokkal.

## Infrastruktúra

**Függőség Rögzítés** - Minden függőség mostantól `~=` operátort használ (pl. `langgraph~=0.2.6`). Patch frissítéseket engedélyez, breaking változásokat blokkolja.

**Központosított Naplózás** - `logging_config.py` létrehozása környezet alapú formázókkal:
- Fejlesztés: részletes formátum sorszámokkal
- Éles: egyszerű formátum
- Biztonsági naplók: WARNING+ szint
- Harmadik fél naplók: csökkentett zajszint

Integrálva az alkalmazás indulásakor a `setup_logging()` függvényen keresztül.

## Dokumentáció

**Architektúra Dokumentáció** - `docs/ARCHITECTURE.md` hozzáadva (10KB) tartalommal:
- 3 Mermaid diagram (rendszer, üzenet folyam, kutatási ügynök folyam)
- Komponens leírások (orchestrator, specialisták, frontend)
- Biztonsági architektúra szekció
- Telepítési minták (helyi/Cloud Run)
- Bővítési útmutató új specialistákhoz

## Módosított Fájlok

**Új:**
- `backend/src/utils/prompt_validator.py`
- `backend/src/utils/logging_config.py`
- `backend/tests/test_rate_limiting.py`
- `backend/tests/test_prompt_validation.py`
- `backend/tests/test_research_integration.py`
- `backend/tests/test_logging_config.py`
- `docs/ARCHITECTURE.md`

**Módosított:**
- `backend/pyproject.toml` - slowapi hozzáadva, minden függőség rögzítve
- `backend/src/app.py` - Sebességkorlátozó, naplózás, validátor integrálva
- `backend/src/utils/middleware.py` - Biztonsági naplózás hozzáadva
- `README.dev.md` - Függőségkezelés dokumentálva

## Konfiguráció

Új opcionális környezeti változók:
- `LOG_LEVEL` - Naplózási részletesség (alapértelmezett: INFO)
- `API_KEY` - API hitelesítés (opcionális, már szerepelt a .env.example-ben)
