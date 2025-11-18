import json
from types import SimpleNamespace

from src.specialists import coder_agent


def test_dashscope_chain_absent_without_api_key(monkeypatch):
    monkeypatch.delenv("QWEN_API_KEY", raising=False)
    assert coder_agent._build_dashscope_chain() is None


def test_dashscope_chain_invocation_with_stub_client(monkeypatch):
    monkeypatch.setenv("QWEN_API_KEY", "dummy-key")

    calls = {}

    class _FakeCompletions:
        def create(self, model, temperature, messages, stream):
            calls["model"] = model
            calls["messages"] = messages
            return SimpleNamespace(
                choices=[
                    SimpleNamespace(
                        message=SimpleNamespace(content="print('ok')")
                    )
                ]
            )

    class _FakeClient:
        def __init__(self):
            self.chat = SimpleNamespace(completions=_FakeCompletions())

    def _fake_openai(api_key, base_url):
        calls["api_key"] = api_key
        calls["base_url"] = base_url
        return _FakeClient()

    monkeypatch.setattr(coder_agent, "OpenAI", _fake_openai)

    chain = coder_agent._build_dashscope_chain()
    assert chain is not None

    output = chain.invoke({"language": "Python", "prompt": "írj hello"})

    assert "print('ok')" == output
    assert calls["api_key"] == "dummy-key"
    assert "messages" in calls
    assert calls["messages"][0]["role"] == "system"


def test_fallback_chain_uses_local_stub(monkeypatch):
    monkeypatch.delenv("QWEN_API_KEY", raising=False)
    monkeypatch.setattr(coder_agent, "_HAS_LANGCHAIN_OLLAMA", False)

    class _FakeResponse:
        def __init__(self, payload):
            self._payload = payload

        def read(self):
            return json.dumps(self._payload).encode("utf-8")

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    captured_payloads = []

    def _fake_urlopen(req, timeout=120):
        captured_payloads.append(json.loads(req.data.decode("utf-8")))
        return _FakeResponse({"response": "print('fallback')"})

    monkeypatch.setattr(coder_agent.urllib.request, "urlopen", _fake_urlopen)

    executor = coder_agent.get_coder_agent_executor()
    assert executor is not None

    result = executor.invoke({"language": "Python", "prompt": "teszt"})

    assert "print('fallback')" == result
    assert captured_payloads, "The fallback chain should attempt an HTTP request."
