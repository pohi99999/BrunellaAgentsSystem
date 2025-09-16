# BrunellaAgentSystem - Architektúra és Ügynökök

Ez a dokumentum a BrunellaAgentSystem projekt jelenlegi architektúráját és a benne szereplő ügynökök működését írja le.

## 1. Architektúra: Hierarchikus LangGraph Modell

A rendszer egy **hierarchikus ügynök-modellre** épül. A központi elem egy **Orchestrator** ügynök, amely a bejövő feladatokat értelmezi, és a feladat típusától függően meghívja a megfelelő eszközt vagy specialista al-ügynököt.

- **Fő Logika:** `backend/src/agent/graph.py`

### Főbb Komponensek

1.  **Orchestrator (Fő Ügynök)**
    - **Szerep:** A bejövő kérések fogadása és delegálása.
    - **Működés:** Egy Gemini 1.5 Pro modell segítségével eldönti, hogy a `research_tool`-t vagy a `qwen3_coder_tool`-t hívja meg.

2.  **Eszközök (Tools) - `backend/src/agent/tools.py`**
    - **`research_tool`**: Ez a tool egy hídként funkcionál. Nem maga végzi a kutatást, hanem meghívja a dedikált **Specialista Kutató Al-Ügynököt**.
    - **`qwen3_coder_tool`**: Ez a tool egy valódi API hívást intéz a Qwen3 kódgeneráló modellhez a felhasználó által megadott prompt alapján.

3.  **Specialista Kutató Al-Ügynök - `backend/src/specialists/research_agent/`**
    - **Szerep:** Mélyreható, iteratív kutatás végzése.
    - **Működés:** Egy önálló LangGraph folyamat, amely ciklikusan ismétli a következő lépéseket: keresési kulcsszavak generálása, Google keresés, az eredmények kiértékelése (reflexió), és szükség esetén újabb, pontosító keresések indítása.

## 2. Javaslat: Jules AI Ügynök Integrációja

A kérésednek megfelelően megvizsgáltam a Jules AI ügynök integrálásának lehetőségét. A véleményem az, hogy **az integráció erősen javasolt**, és jelentősen növelné a projekt képességeit és megbízhatóságát.

### Miért érdemes integrálni?

- **Specializált Képesség:** Jules egy kifejezetten kódírásra és tesztelésre specializált ügynök. A napi 300 tesztelési kapacitása lehetővé teszi a folyamatos, automatizált minőségellenőrzést.
- **Architekturális Illeszkedés:** Tökéletesen illeszkedik a jelenlegi hierarchikus modellbe, mint egy új, fejlett "eszköz" vagy "specialista", amit az Orchestrator meghívhat.

### Javasolt Felhasználási Módok

1.  **Automatizált Tesztírás:**
    - **Folyamat:** Az Orchestrator egy új `test_writer_tool` eszközt kapna, ami Jules-t hívja meg. Egy új funkció implementálása után az Orchestrator automatikusan megbízhatná Jules-t, hogy írjon `pytest` teszteket az új kódhoz.
    - **Eredmény:** Folyamatosan magas tesztlefedettség és megbízhatóbb kód.

2.  **Fejlett Kódgenerálás:**
    - **Folyamat:** A `qwen3_coder_tool` mellett (vagy helyett) Jules is bekerülhetne mint kódoló ügynök. Az Orchestrator akár dönthetne is a feladat komplexitása alapján, hogy a gyorsabb Qwen3-at vagy a vélhetően alaposabb Jules-t hívja meg.
    - **Eredmény:** Magasabb minőségű, komplexebb kódok generálásának képessége.

Jules integrálása a következő logikus lépés a rendszer "intelligensebbé" és önállóbbá tételéhez.