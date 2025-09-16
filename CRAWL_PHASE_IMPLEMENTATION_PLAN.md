# Implementációs Terv: "Crawl" Fázis

**Cél:** A Qwen3 kódoló ügynök gyors, helyi fejlesztői környezetben történő integrációja a `BrunellaAgentSystem`-be az Ollama eszköz segítségével.

---

### 1. Lépés: Előkészületek - Ollama Telepítése és Futtatása

Az Ollama egy eszköz, amely rendkívül egyszerűvé teszi a nyílt forráskódú LLM-ek futtatását a saját gépeden. A LangChain beépített támogatással rendelkezik hozzá.

1.  **Telepítsd az Ollama-t:**
    -   Látogass el az [ollama.com](https://ollama.com) weboldalra, és töltsd le a Windows-nak megfelelő telepítőt, majd telepítsd.

2.  **Töltsd le és futtasd a Qwen3 modellt:**
    -   Nyiss egy új parancssort (terminált), és futtasd a következő parancsot. Ez letölti a Qwen3 modell egy kisebb, fejlesztésre ideális 7 milliárd paraméteres változatát, és elindítja a háttérben egy helyi szerveren.
    ```bash
    ollama run qwen3:7b
    ```
    -   Amint a parancs lefutott, az Ollama a háttérben futni fog, és a modell elérhető lesz egy helyi API-n keresztül (`http://localhost:11434`).

### 2. Lépés: Backend Függőségek Bővítése

Ahhoz, hogy a Python kódunk kommunikálni tudjon az Ollama szerverrel, hozzá kell adnunk egy új függőséget a projekthez.

1.  **Nyisd meg a `backend/pyproject.toml` fájlt.**
2.  A `[project.dependencies]` szekcióban adj hozzá egy új sort:
    ```toml
    "langchain-ollama"
    ```
3.  Mentsd el a fájlt, majd a `backend` könyvtárban futtass egy `pip install -e .` parancsot a virtuális környezetben, hogy települjön az új csomag.

### 3. Lépés: A Kódoló Specialista Ügynök Létrehozása

Most létrehozzuk azt a Python modult, ami a Qwen3 kódoló ügynököt képviseli a rendszerünkben.

1.  **Hozd létre a következő fájlt:** `backend/src/specialists/coder_agent.py`
2.  **Illeszd be a következő kódot a fájlba:**

    ```python
    # backend/src/specialists/coder_agent.py

    from langchain_ollama.chat_models import ChatOllama
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.output_parsers import StrOutputParser

    # Rendszer-prompt, ami instruálja a modellt, hogy viselkedjen kódolóként
    CODE_GENERATION_SYSTEM_PROMPT = """
    Te egy specializált, nyílt forráskódú kódgeneráló AI vagy, a Qwen3-coder.
    Kizárólagos feladatod, hogy a kapott prompt alapján magas minőségű, tiszta és hatékony kódot generálj a megadott programozási nyelven.
    - NE adj magyarázatot a kódhoz.
    - NE használj markdown formázást (pl. ```python).
    - NE írj semmilyen üdvözlő vagy bevezető szöveget.
    - Csak és kizárólag a kért kódot add vissza.
    - Ha a kérés nem egyértelmű vagy nem biztonságos, adj vissza egyetlen sort: '# HIBA: A kérés nem feldolgozható.'
    """

    def get_coder_agent_executor():
        """
        Létrehozza és visszaadja a Qwen3 kódoló ügynököt,
        ami egy egyszerű, Ollama-alapú LangChain lánc.
        """
        # Csatlakozás a lokálisan futó Ollama-n keresztül a qwen3 modellhez
        llm = ChatOllama(model="qwen3:7b", temperature=0)

        # Prompt sablon létrehozása
        prompt = ChatPromptTemplate.from_messages([
            ("system", CODE_GENERATION_SYSTEM_PROMPT),
            ("human", "Programozási nyelv: {language}\n\nFeladat: {prompt}"),
        ])

        # A lánc összeállítása: Prompt -> LLM -> Kimenet (string)
        chain = prompt | llm | StrOutputParser()

        return chain

    # Létrehozunk egy példányt, amit a fő graph importálni tud
    coder_chain = get_coder_agent_executor()
    ```

### 4. Lépés: Integráció a Fő Ügynökbe (LangGraph)

Ez a lépés koncepcionális, mivel a `backend/src/agent/` könyvtár pontos tartalmát nem olvastam be, de az elv a következő:

1.  A fő LangGraph folyamatot definiáló scriptben (pl. `backend/src/agent/graph.py`) importálni kell az újonnan létrehozott kódoló láncot:
    ```python
    from specialists.coder_agent import coder_chain
    ```
2.  A LangGraph-ban létre kell hozni egy új "node"-ot (csomópontot), ami meghívja ezt a `coder_chain`-t a megfelelő bemenettel (a kódolási feladat leírásával).
3.  Az orchestrator ügynököt (a router-t a gráfban) fel kell készíteni arra, hogy a kódolással kapcsolatos kéréseket ehhez az új csomóponthoz irányítsa.

### 5. Lépés: Tesztelés és Validáció

Miután az integráció megtörtént, futtass egy egyszerű tesztet a rendszeren keresztül:

-   **Indítsd el a teljes rendszert** a `docker-compose.yml` vagy a `run-stack.bat` segítségével.
-   **A frontend felületen** add a következő utasítást a központi ügynöknek:
    > "Kérd meg a kódoló specialistát, hogy írjon egy Python függvényt `hello_world` néven, ami visszaadja a 'hello world' stringet."

-   **Várt eredmény:** A rendszernek a `coder_chain`-t kell meghívnia, és a kimenetnek a következő tiszta Python kódnak kell lennie:
    ```python
    def hello_world():
        return "hello world"
    ```

---

Ezzel a tervvel az integráció első, működőképes verziója gyorsan és hatékonyan létrehozható a helyi fejlesztői gépen.
