flowchart TD

    A[Brunella Agent\nProjektmenedzser] -->|Feladat delegálás| B[Researcher Agent\nKutató]
    B -->|Összegyűjtött információ| C[Coder Agent\nKódoló]
    C -->|Megírt kód/specifikáció| D[QA Agent\nMinőségellenőr]
    D -->|Visszajelzés, hibák, jóváhagyás| A

    subgraph Backend
    A
    B
    C
    D
    end

    A -.->|Eredmény| User[(Felhasználó)]
    User -->|Új utasítás / prompt| A
##Magyarázat

Brunella → központi projektmenedzser, ő indítja és koordinálja a folyamatot.

Researcher → begyűjti a szükséges információkat (pl. AI technológiák, kódminták).

Coder → a kutatás alapján implementálja a kódot (Python/FastAPI).

QA → ellenőrzi a kód minőségét, hibákat keres, visszajelzést ad.

Loop → ha hibát talál a QA, visszaküldi a feladatot Brunellának, aki újraosztja.

Felhasználó → külső utasításokat ad, és a végén megkapja az eredményt.

⚙️ Kiegészítés

A háttérben:

LangGraph kezeli az állapotátmeneteket és a checkpointokat.

SQLite memória (brunella_memory.db) segít a hosszú távú kontextus megőrzésében.

Backend API (run_server.py, backend/) teszi elérhetővé a funkciókat külső hívásokhoz.