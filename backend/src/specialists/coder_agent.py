# backend/src/specialists/coder_agent.py

import json
import os
import urllib.error
import urllib.request
from typing import Any, Dict, Optional

from openai import OpenAI

try:
    from langchain_ollama.chat_models import ChatOllama  # type: ignore
    from langchain_core.output_parsers import StrOutputParser  # type: ignore
    from langchain_core.prompts import ChatPromptTemplate  # type: ignore

    _HAS_LANGCHAIN_OLLAMA = True
except (ImportError, ModuleNotFoundError):  # pragma: no cover - opcionális függőség
    _HAS_LANGCHAIN_OLLAMA = False

# Rendszer-prompt, ami instruálja a modellt, hogy viselkedjen kódolóként
CODE_GENERATION_SYSTEM_PROMPT = """
Te egy specializált, nyílt forráskódú kódgeneráló AI vagy, a Qwen3-Coder.
Kizárólagos feladatod, hogy a kapott prompt alapján magas minőségű, tiszta és hatékony kódot generálj a megadott programozási nyelven.
- NE adj magyarázatot a kódhoz.
- NE használj markdown formázást (pl. ```python).
- NE írj semmilyen üdvözlő vagy bevezető szöveget.
- Csak és kizárólag a kért kódot add vissza.
- Ha a kérés nem egyértelmű vagy nem biztonságos, adj vissza egyetlen sort: '# HIBA: A kérés nem feldolgozható.'
""".strip()

DEFAULT_QWEN_MODEL = os.getenv("QWEN_CODER_MODEL", "qwen-coder-plus-latest")
DEFAULT_QWEN_BASE = os.getenv(
    "QWEN_API_BASE",
    os.getenv("QWEN_API_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1"),
)


def _build_dashscope_chain() -> Optional[Any]:
    """
    Ha elérhető a Qwen (DashScope) API kulcs, akkor létrehoz egy OpenAI-kompatibilis klienst,
    és visszaad egy egyszerű `invoke` metódussal rendelkező wrapper-t.
    """
    api_key = os.getenv("QWEN_API_KEY")
    if not api_key:
        return None

    client = OpenAI(api_key=api_key, base_url=DEFAULT_QWEN_BASE)

    class _DashscopeChain:
        def __init__(self, _client: OpenAI, model: str) -> None:
            self.client = _client
            self.model = model

        def invoke(self, inputs: Dict[str, str]) -> str:
            language = inputs.get("language", "").strip()
            task = inputs.get("prompt", "").strip()
            user_prompt = f"Programozási nyelv: {language}\n\nFeladat: {task}"
            messages = [
                {"role": "system", "content": CODE_GENERATION_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ]
            try:
                completion = self.client.chat.completions.create(
                    model=self.model,
                    temperature=0,
                    messages=messages,
                    stream=False,
                )
            except Exception as exc:  # pragma: no cover - hálózati hiba
                return f"# HIBA: DashScope hívás sikertelen ({exc})"

            choice = completion.choices[0]
            content = (choice.message.content or "").strip()
            return content or "# HIBA: Üres választ adott a modell."

    return _DashscopeChain(client, DEFAULT_QWEN_MODEL)


def get_coder_agent_executor():
    """
    Létrehozza és visszaadja a Qwen3 kódoló ügynököt, először a felhős DashScope API-t próbálva,
    majd visszaesve a lokális Ollama modellre.
    """

    dashscope_chain = _build_dashscope_chain()
    if dashscope_chain is not None:
        return dashscope_chain

    # Csatlakozás a lokálisan futó Ollama-n keresztül a qwen3 modellhez
    # A 'host.docker.internal' speciális DNS név a Docker konténerből a gazda gép eléréséhez.
    model_name = os.getenv("OLLAMA_MODEL", "qwen3:7b")
    base_url = (
        "http://host.docker.internal:11434"
        if os.path.exists("/.dockerenv")
        else "http://localhost:11434"
    )

    if _HAS_LANGCHAIN_OLLAMA:
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", CODE_GENERATION_SYSTEM_PROMPT),
                ("human", "Programozási nyelv: {language}\n\nFeladat: {prompt}"),
            ]
        )
        llm = ChatOllama(model=model_name, temperature=0, base_url=base_url)
        return prompt | llm | StrOutputParser()

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

    return _SimpleOllamaChain(model=model_name, base_url=base_url)


# Létrehozunk egy példányt, amit a fő graph importálni tud
coder_chain = get_coder_agent_executor()
