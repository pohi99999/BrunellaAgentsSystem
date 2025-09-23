# backend/src/specialists/coder_agent.py

import os

try:
    from langchain_ollama.chat_models import ChatOllama  # type: ignore
    from langchain_core.prompts import ChatPromptTemplate  # type: ignore
    from langchain_core.output_parsers import StrOutputParser  # type: ignore
    _HAS_LANGCHAIN_OLLAMA = True
except Exception:
    _HAS_LANGCHAIN_OLLAMA = False

import json
import urllib.request
import urllib.error

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

class _SimpleOllamaChain:
    def __init__(self, model: str, base_url: str):
        self.model = model
        self.base_url = base_url.rstrip("/")

    def invoke(self, inputs: dict) -> str:
        language = inputs.get("language", "")
        task = inputs.get("prompt", "")
        full_prompt = f"{CODE_GENERATION_SYSTEM_PROMPT}\n\nProgramozási nyelv: {language}\n\nFeladat: {task}"
        payload = {
            "model": self.model,
            "prompt": full_prompt,
            "stream": False,
            "options": {"temperature": 0},
        }
        req = urllib.request.Request(
            url=f"{self.base_url}/api/generate",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data.get("response", "")
        except urllib.error.HTTPError as e:
            return f"# HIBA: HTTP {e.code} {e.reason}"
        except Exception as e:  # pragma: no cover
            return f"# HIBA: {e}"

def get_coder_agent_executor():
    """
    Létrehozza és visszaadja a Qwen3 kódoló ügynököt,
    ami egy egyszerű, Ollama-alapú LangChain lánc.
    """
    # Csatlakozás a lokálisan futó Ollama-n keresztül a qwen3 modellhez
    # A 'host.docker.internal' speciális DNS név a Docker konténerből a gazda gép eléréséhez.
    model_name = os.getenv("OLLAMA_MODEL", "qwen3:7b")
    base_url = (
        "http://host.docker.internal:11434"
        if os.path.exists("/.dockerenv")
        else "http://localhost:11434"
    )

    if _HAS_LANGCHAIN_OLLAMA:
        prompt = ChatPromptTemplate.from_messages([
            ("system", CODE_GENERATION_SYSTEM_PROMPT),
            ("human", "Programozási nyelv: {language}\n\nFeladat: {prompt}"),
        ])
        llm = ChatOllama(model=model_name, temperature=0, base_url=base_url)
        return prompt | llm | StrOutputParser()

    return _SimpleOllamaChain(model=model_name, base_url=base_url)

# Létrehozunk egy példányt, amit a fő graph importálni tud
coder_chain = get_coder_agent_executor()
