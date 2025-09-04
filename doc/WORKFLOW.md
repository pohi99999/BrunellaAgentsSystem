# Gemini Fullstack LangGraph Quickstart

This project demonstrates a fullstack application using a React frontend and a LangGraph-powered backend agent. The agent is designed to perform comprehensive research on a user's query by dynamically generating search terms, querying the web using Google Search, reflecting on the results to identify knowledge gaps, and iteratively refining its search until it can provide a well-supported answer with citations. This application serves as an example of building research-augmented conversational AI using LangGraph and Google's Gemini models.

<img src="./app.png" title="Gemini Fullstack LangGraph" alt="Gemini Fullstack LangGraph" width="90%">

## Features

- 💬 Fullstack application with a React frontend and LangGraph backend.
- 🧠 Powered by a LangGraph agent for advanced research and conversational AI.
- 🔍 Dynamic search query generation using Google Gemini models.
- 🌐 Integrated web research via Google Search API.
- 🤔 Reflective reasoning to identify knowledge gaps and refine searches.
- 📄 Generates answers with citations from gathered sources.
- 🔄 Hot-reloading for both frontend and backend during development.

## Project Structure

The project is divided into two main directories:

-   `frontend/`: Contains the React application built with Vite.
-   `backend/`: Contains the LangGraph/FastAPI application, including the research agent logic.

## Getting Started: Development and Local Testing

Follow these steps to get the application running locally for development and testing.

**1. Prerequisites:**

-   Node.js and npm (or yarn/pnpm)
-   Python 3.11+
-   **`GEMINI_API_KEY`**: The backend agent requires a Google Gemini API key.
    1.  Navigate to the `backend/` directory.
    2.  Create a file named `.env` by copying the `backend/.env.example` file.
    3.  Open the `.env` file and add your Gemini API key: `GEMINI_API_KEY="YOUR_ACTUAL_API_KEY"`

**2. Install Dependencies:**

**Backend:**

```bash
cd backend
pip install .
```

**Frontend:**

```bash
cd frontend
npm install
```

**3. Run Development Servers:**

**Backend & Frontend:**

```bash
make dev
```
This will run the backend and frontend development servers.    Open your browser and navigate to the frontend development server URL (e.g., `http://localhost:5173/app`).

_Alternatively, you can run the backend and frontend development servers separately. For the backend, open a terminal in the `backend/` directory and run `langgraph dev`. The backend API will be available at `http://127.0.0.1:2024`. It will also open a browser window to the LangGraph UI. For the frontend, open a terminal in the `frontend/` directory and run `npm run dev`. The frontend will be available at `http://localhost:5173`._

### Windows (PowerShell) Troubleshooting & Helper Scripts

On Windows, the `langgraph` CLI might not be found even after installation if you are in a different Python version or the virtual environment is not activated. We created / use a Python 3.11 virtual environment named `.venv311` at the project root.

Quick commands (PowerShell):

```powershell
# Create env (already done once)
py -3.11 -m venv .venv311

# Activate it
./.venv311/Scripts/Activate.ps1

# Install backend (editable) with dev extras
pip install -e backend/[dev]

# If langgraph command still not found, invoke via explicit path
./.venv311/Scripts/langgraph.exe dev --config backend/langgraph.json

# Or (module form if needed)
python -m langgraph_cli.main dev --config backend/langgraph.json
```

If you only want a plain FastAPI server (no LangGraph UI) you can run:

```powershell
python run_server.py  # serves at http://127.0.0.1:8000
```

Then set `apiUrl` in `frontend/src/App.tsx` to `http://localhost:8000/agent` (or adjust routes accordingly) until the LangGraph dev server works on 2024.

### Current Progress Log (Automated Update)

This section is appended by the assistant to track implementation progress:

| Date (UTC) | Change | Notes |
|------------|--------|-------|
| 2025-08-29 | Added troubleshooting section & PowerShell steps | `langgraph` CLI not resolving; use explicit path/module fallback. |
| 2025-08-29 | Verified backend graph & tools structure | Graph compiles; research specialist loaded. |
| 2025-08-29 | Added guidance for plain uvicorn fallback | Use `run_server.py` on port 8000 if dev server blocked. |
| 2025-08-29 | Added helper scripts | `backend/scripts/start_langgraph_dev.ps1` and `diagnose_cli.py`. |

Next Planned Steps:

1. Ensure `langgraph` CLI executable exists at `./.venv311/Scripts/langgraph.exe`.
2. Launch dev server on port 2024 and validate `/agent` endpoint streaming.
3. Add minimal automated test script for CLI invocation.
4. (Optional) Remove unused dependency `google-cloud-managed-identities` if not leveraged.

If picking up after this point, start by activating the venv and trying the explicit path to `langgraph.exe` as shown above.

## How the Backend Agent Works (High-Level)

The core of the backend is a LangGraph agent defined in `backend/src/agent/graph.py`. It follows these steps:

<img src="./agent.png" title="Agent Flow" alt="Agent Flow" width="50%">

1.  **Generate Initial Queries:** Based on your input, it generates a set of initial search queries using a Gemini model.
2.  **Web Research:** For each query, it uses the Gemini model with the Google Search API to find relevant web pages.
3.  **Reflection & Knowledge Gap Analysis:** The agent analyzes the search results to determine if the information is sufficient or if there are knowledge gaps. It uses a Gemini model for this reflection process.
4.  **Iterative Refinement:** If gaps are found or the information is insufficient, it generates follow-up queries and repeats the web research and reflection steps (up to a configured maximum number of loops).
5.  **Finalize Answer:** Once the research is deemed sufficient, the agent synthesizes the gathered information into a coherent answer, including citations from the web sources, using a Gemini model.

## CLI Example

For quick one-off questions you can execute the agent from the command line. The
script `backend/examples/cli_research.py` runs the LangGraph agent and prints the
final answer:

```bash
cd backend
python examples/cli_research.py "What are the latest trends in renewable energy?"
```


## Deployment

In production, the backend server serves the optimized static frontend build. LangGraph requires a Redis instance and a Postgres database. Redis is used as a pub-sub broker to enable streaming real time output from background runs. Postgres is used to store assistants, threads, runs, persist thread state and long term memory, and to manage the state of the background task queue with 'exactly once' semantics. For more details on how to deploy the backend server, take a look at the [LangGraph Documentation](https://langchain-ai.github.io/langgraph/concepts/deployment_options/). Below is an example of how to build a Docker image that includes the optimized frontend build and the backend server and run it via `docker-compose`.

_Note: For the docker-compose.yml example you need a LangSmith API key, you can get one from [LangSmith](https://smith.langchain.com/settings)._

_Note: If you are not running the docker-compose.yml example or exposing the backend server to the public internet, you should update the `apiUrl` in the `frontend/src/App.tsx` file to your host. Currently the `apiUrl` is set to `http://localhost:8123` for docker-compose or `http://localhost:2024` for development._

**1. Build the Docker Image:**

   Run the following command from the **project root directory**:
   ```bash
   docker build -t gemini-fullstack-langgraph -f Dockerfile .
   ```
**2. Run the Production Server:**

   ```bash
   GEMINI_API_KEY=<your_gemini_api_key> LANGSMITH_API_KEY=<your_langsmith_api_key> docker-compose up
   ```

Open your browser and navigate to `http://localhost:8123/app/` to see the application. The API will be available at `http://localhost:8123`.

## Technologies Used

- [React](https://reactjs.org/) (with [Vite](https://vitejs.dev/)) - For the frontend user interface.
- [Tailwind CSS](https://tailwindcss.com/) - For styling.
- [Shadcn UI](https://ui.shadcn.com/) - For components.
- [LangGraph](https://github.com/langchain-ai/langgraph) - For building the backend research agent.
- [Google Gemini](https://ai.google.dev/models/gemini) - LLM for query generation, reflection, and answer synthesis.

## License

This project is licensed under the Apache License 2.0. See the [LICENSE](LICENSE) file for details.
 
---------------------------------------------------------------------------

##1. LLM és környezet

Provider: openai (valójában a Qwen 2.5 coder 32B instruct modellt hívja az Alibaba Dashscope kompatibilis endpointján keresztül).

Model: qwen2.5-coder-32b-instruct

API endpoint: https://dashscope.aliyuncs.com/compatible-mode/v1

Hitelesítés: OPENAI_API_KEY environment variable-ből töltve.

##2. Memória modul

Engedélyezve: Igen

Típus: SQLite

Fájl: ./brunella_memory.db
Ez a helyi állapotmegőrzés (kontextus és feladatkövetés) alapja.

##3. Multi-Agent architektúra

Négy ügynök van definiálva, mindegyiknek világos szerepköre és narratívája:

#Brunella (Projektmenedzser)

Koordinálja a csapatot

Feladatokat delegál

Ez a központi irányító ügynök

#Researcher (Kutató ügynök)

AI architektúrákról és új technológiákról gyűjt adatokat

Ez szolgáltatja az inputot a többieknek

#Coder (Kódoló ügynök)

Specifikáció alapján Python és FastAPI kódot ír

Fő implementációs motor

#QA (Minőségellenőr)

Átnézi a kódot

Hibákat keres, visszajelzést ad

Kritikus szem a végén

##4. Kapcsolódó dokumentumok

A korábban csatolt fájlokból:

agent_backend.py → Flask alapú backend, integráció Gmail, Drive, Calendar, Docs, Sheets API-kkal.

AI Ügynökfejlesztés - Hatékony Promptok és Megbízh.md → Stratégiai prompt engineering és ügynök-minták (ROCTTOC, ReAct, Multi-Agent Loop).

##emlek.md → Memória-helyreállítási protokoll, ami megerősíti, hogy Brunella a stratégiai koordinátor szerepben fut.

Összegzés: Projekt állapota

Az alap multi-agent konfiguráció kész (Brunella + researcher + coder + QA).

A backend fut, API endpointok előkészítve (pl. /command).

Van memóriarendszer (SQLite) a kontextus kezelésére.

A prompt engineering stratégiák dokumentálva, integrálásra készek.

Következő lépés: a workflow-k összekötése → vagyis hogy a Brunella agent ténylegesen meghívja a researcher → coder → QA láncot, és az eredmény bekerüljön a backend logikába.

------------------------------------------

🌐 Gyökér (G:\Brunella\BrunellaAgentSystem\)

Konfiguráció és futtatás

.env, .gitignore, config.yaml (ügynök + memória setup)

docker-compose.yml, Makefile, run-stack.bat, stop-stack.bat, run_server.py

Dokumentáció / vizuálok

README.md, agent.png, app.png

Indítási belépési pont

main.py

🖥️ VS Code beállítások

.vscode/settings.json

⚙️ Backend

/backend

.env, .env.example, Dockerfile, pyproject.toml

langgraph, langgraph.json → ez valószínűleg a LangGraph konfiguráció

test-agent.ipynb → Jupyter notebook teszteléshez

run-backend.bat → Windows futtatási script

Checkpoints: .langgraph_api/ (itt mentődnek az ügynök állapotok: store.pckl, vectors.pckl stb.)

Virtuális környezet: .venv311/ → telepített dependency-k (fastapi, crewai, google-ai stb.)

--------------------------

BrunellaAgentSystem/
├── .env
├── .gitignore
├── agent.png
├── app.png
├── config.yaml                # Ügynök + memória konfiguráció
├── docker-compose.yml         # Konténerizált stack
├── LICENSE
├── main.py                    # Belépési pont
├── Makefile
├── README.md
├── run-stack.bat              # Stack indítás Windows alatt
├── run_server.py              # Backend indítás
├── stop-stack.bat             # Stack leállítás
├── struktur.txt               # Könyvtárfa export
│
├── .vscode/
│   └── settings.json          # Fejlesztői beállítások
│
└── backend/
    ├── .env
    ├── .env.example
    ├── .gitignore
    ├── Dockerfile
    ├── langgraph              # LangGraph konfig és logika
    ├── langgraph.json
    ├── LICENSE
    ├── Makefile
    ├── pyproject.toml         # Python csomagkezelés
    ├── run-backend.bat
    ├── test-agent.ipynb       # Jupyter notebook (ügynök teszteléshez)
    │
    ├── .langgraph_api/        # Állapot checkpointok
    │   ├── .langgraph_checkpoint.1.pckl
    │   ├── .langgraph_checkpoint.2.pckl
    │   ├── store.pckl
    │   ├── store.vectors.pckl
    │   └── ...
    │
    └── .venv311/              # Virtuális környezet + dependency-k
        ├── pyvenv.cfg
        ├── Include/
        ├── Lib/
        │   └── site-packages/ (FastAPI, crewai, google-ai stb.)
        └── ...
yökérben: konfigurációs fájlok, indító scriptek, dokumentáció.

Backend mappa: tényleges AI agent logika + LangGraph + notebookok.

.langgraph_api/: az ügynökök állapotának checkpointjai (ez jelzi, hogy a rendszer már futott és dolgozott).

.venv311/: a Python környezet minden szükséges könyvtárral.

Így a projekt futtatható, bővíthető és tesztelhető állapotban van.

2025.09.04. -i állapot. 

#Bejegyzés vége.

----------------------------------------------------------------------------------------

