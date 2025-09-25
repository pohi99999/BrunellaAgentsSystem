# BrunellaAgentsSystem: Projekt Áttekintés

Ez a dokumentum a projekt központi összefoglalója, amely a rendrakás utáni, tiszta állapotot tükrözi.

## 1. A Projekt Célja

A **BrunellaAgentsSystem** egy fejlett, több-ügynökös mesterséges intelligencia rendszer. A célja, hogy komplex feladatokat (pl. adatelemzés, kódgenerálás, kutatás) képes legyen autonóm módon lebontani, delegálni specializált AI ágenseknek, és a végeredményt felügyelni.

## 2. Architektúra

A rendszer két fő komponensből áll:

### Backend

- **Helye:** `/backend` könyvtár
- **Technológia:** Python, [FastAPI](https://fastapi.tiangolo.com/), [LangGraph](https://langchain-ai.github.io/langgraph/)
- **Működés:** Egy hierarchikus ügynök-rendszert valósít meg, ahol egy központi "orchestrator" fogadja a kéréseket, és a feladat típusától függően továbbítja azokat a megfelelő "specialista" ügynöknek.
- **API:** Egy `/agent` végpontot tesz közzé, amelyen keresztül a frontend kommunikál a rendszerrel.

### Frontend

- **Helye:** `/frontend` könyvtár
- **Technológia:** React (JavaScript), [Vite](https://vitejs.dev/)
- **Működés:** Egy egyszerű, letisztult felhasználói felületet biztosít, ahol a felhasználó interakcióba léphet az AI rendszerrel. A frontend a backend `/agent` végpontjára küldi a kéréseket és valós időben megjeleníti a kapott válaszokat.

## 3. Működtetés és Fejlesztés

A projekt egységesített eszközöket használ a fejlesztés és a futtatás támogatására.

- **Konténerizáció:** A `docker-compose.yml` fájl definiálja a teljes alkalmazás-stack (backend, frontend) konténerizált futtatását, biztosítva a konzisztens környezetet.
- **Workflow Automatizálás:** A `Makefile` egyszerű parancsokat (`make build`, `make up`, `make down` stb.) biztosít a gyakori fejlesztési feladatok (pl. buildelés, konténerek indítása) elvégzésére.
- **Konfiguráció:** A rendszer központi beállításait a `config.yaml` fájl tartalmazza. Itt lehet konfigurálni például a használt AI modelleket vagy az API kulcsokat.

## 4. Verziókezelés

- A projekt a **Git** verziókezelőt használja.
- A `.gitignore` fájl megfelelően be van állítva, hogy a fejlesztés során generált felesleges fájlok (virtuális környezetek, build- арtefaktumok, logok) ne kerüljenek be a tárolóba.

## 5. Archivált Elemek

Az `_archive` könyvtár tartalmazza a projekt korábbi, redundáns vagy elavult fájljait. Ezeket a tisztítás során különítettük el, és a későbbiekben törölhetők, miután megbizonyosodtunk róla, hogy semmi sem hiányzik a jelenlegi működő rendszerből.
