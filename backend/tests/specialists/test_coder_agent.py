import os
import sys
import pytest
from unittest.mock import patch, MagicMock

# Ensure we can import from the backend/src module directly
CURRENT_DIR = os.path.dirname(__file__)
BACKEND_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "../.."))
if BACKEND_ROOT not in sys.path:
    sys.path.insert(0, BACKEND_ROOT)

from src.specialists import coder_agent

def test_get_coder_agent_executor_with_langchain():
    """
    Tests the get_coder_agent_executor function when langchain-ollama is available.
    """
    with patch('src.specialists.coder_agent._HAS_LANGCHAIN_OLLAMA', True):
        executor = coder_agent.get_coder_agent_executor()
        assert executor is not None
        # We can't easily assert the type since it's a composed chain,
        # but we can check that it's not our fallback class.
        assert not isinstance(executor, coder_agent._SimpleOllamaChain)

def test_get_coder_agent_executor_without_langchain():
    """
    Tests the get_coder_agent_executor function when langchain-ollama is not available.
    """
    with patch('src.specialists.coder_agent._HAS_LANGCHAIN_OLLAMA', False):
        executor = coder_agent.get_coder_agent_executor()
        assert executor is not None
        assert isinstance(executor, coder_agent._SimpleOllamaChain)

def test_simple_ollama_chain_invoke():
    """
    Tests the invoke method of the _SimpleOllamaChain class.
    """
    with patch('src.specialists.coder_agent._HAS_LANGCHAIN_OLLAMA', False):
        # Mock the urlopen call to avoid real HTTP requests
        mock_response = MagicMock()
        mock_response.read.return_value = b'{"response": "def hello():\\n  return \\"hello\\""}'
        mock_response.__enter__.return_value = mock_response

        with patch('urllib.request.urlopen', return_value=mock_response) as mock_urlopen:
            executor = coder_agent.get_coder_agent_executor()
            result = executor.invoke({"language": "python", "prompt": "write a hello function"})

            assert result == 'def hello():\n  return "hello"'
            mock_urlopen.assert_called_once()

def test_simple_ollama_chain_invoke_http_error():
    """
    Tests the invoke method of the _SimpleOllamaChain class when an HTTPError occurs.
    """
    with patch('src.specialists.coder_agent._HAS_LANGCHAIN_OLLAMA', False):
        # Mock urlopen to raise an HTTPError
        from urllib.error import HTTPError
        with patch('urllib.request.urlopen', side_effect=HTTPError("url", 404, "Not Found", {}, None)) as mock_urlopen:
            executor = coder_agent.get_coder_agent_executor()
            result = executor.invoke({"language": "python", "prompt": "write a hello function"})

            assert result == "# HIBA: HTTP 404 Not Found"
            mock_urlopen.assert_called_once()
