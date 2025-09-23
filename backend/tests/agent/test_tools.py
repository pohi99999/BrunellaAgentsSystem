import os
import sys
import pytest
from unittest.mock import patch, MagicMock

# Ensure we can import from the backend/src module directly
CURRENT_DIR = os.path.dirname(__file__)
BACKEND_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "../.."))
if BACKEND_ROOT not in sys.path:
    sys.path.insert(0, BACKEND_ROOT)

# Since the tools are initialized at module level, we need to patch the dependencies before importing them
@pytest.fixture(autouse=True)
def mock_dependencies():
    with patch('src.agent.tools.research_graph'), \
         patch('src.agent.tools.coder_chain'):
        yield

from src.agent.tools import research_tool, qwen3_coder_tool
from langchain_core.messages import HumanMessage

@patch('src.agent.tools.research_graph')
def test_research_tool(mock_research_graph):
    """Tests the research_tool function."""
    # Arrange
    mock_research_graph.invoke.return_value = {"messages": [HumanMessage(content="research result")]}
    query = "test query"

    # Act
    result = research_tool.invoke({"query": query})

    # Assert
    mock_research_graph.invoke.assert_called_once_with({"messages": [HumanMessage(content=query)]})
    assert result == "research result"

@patch('src.agent.tools.coder_chain')
def test_qwen3_coder_tool(mock_coder_chain):
    """Tests the qwen3_coder_tool function."""
    # Arrange
    mock_coder_chain.invoke.return_value = "def hello():\n  return 'hello'"
    language = "python"
    prompt = "write a hello function"

    # Act
    result = qwen3_coder_tool.invoke({"language": language, "prompt": prompt})

    # Assert
    mock_coder_chain.invoke.assert_called_once_with({"language": language, "prompt": prompt})
    assert result == "def hello():\n  return 'hello'"

@patch('src.agent.tools.coder_chain')
def test_qwen3_coder_tool_with_error(mock_coder_chain):
    """Tests the qwen3_coder_tool function when an error occurs."""
    # Arrange
    mock_coder_chain.invoke.side_effect = Exception("test error")
    language = "python"
    prompt = "write a hello function"

    # Act
    result = qwen3_coder_tool.invoke({"language": language, "prompt": prompt})

    # Assert
    mock_coder_chain.invoke.assert_called_once_with({"language": language, "prompt": prompt})
    assert result == "# Error invoking coder agent: test error"
