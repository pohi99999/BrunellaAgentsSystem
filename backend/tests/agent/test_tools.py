import os
import pytest
from unittest.mock import patch, MagicMock

with patch.dict(os.environ, {"GEMINI_API_KEY": "test_key"}), \
     patch("backend.src.specialists.research_agent.graph.Client"):
    from backend.src.agent.tools import research_tool, qwen3_coder_tool

from langchain_core.messages import AIMessage, HumanMessage

@patch("backend.src.agent.tools.research_graph")
def test_research_tool(mock_research_graph):
    """
    Tests the research_tool function to ensure it correctly calls the research graph.
    """
    # Arrange
    mock_research_graph.invoke.return_value = {
        "messages": [AIMessage(content="Research result")]
    }

    # Act
    result = research_tool("test query")

    # Assert
    assert result == "Research result"
    mock_research_graph.invoke.assert_called_once()
    # Check that the argument passed to invoke is a dictionary with a "messages" key
    # and the value is a list containing a HumanMessage with the correct content.
    args, kwargs = mock_research_graph.invoke.call_args
    assert "messages" in args[0]
    assert isinstance(args[0]["messages"][0], HumanMessage)
    assert args[0]["messages"][0].content == "test query"

@patch("backend.src.agent.tools.openai.OpenAI")
@patch.dict(os.environ, {"QWEN_API_KEY": "test_key"})
def test_qwen3_coder_tool_success(mock_openai):
    """
    Tests the qwen3_coder_tool for a successful API call.
    """
    # Arrange
    mock_client = MagicMock()
    mock_openai.return_value = mock_client
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "print('Hello, World!')"
    mock_client.chat.completions.create.return_value = mock_response

    # Act
    result = qwen3_coder_tool("create a hello world script")

    # Assert
    assert result == "print('Hello, World!')"
    mock_openai.assert_called_once_with(api_key="test_key", base_url="https://dashscope.aliyuncs.com/compatible-mode/v1")
    mock_client.chat.completions.create.assert_called_once()

def test_qwen3_coder_tool_no_api_key():
    """
    Tests the qwen3_coder_tool when the QWEN_API_KEY is not set.
    """
    # Arrange
    with patch.dict(os.environ, {}, clear=True):
        # Act
        result = qwen3_coder_tool("test query")
        # Assert
        assert "# Error: QWEN_API_KEY environment variable not set." in result

@patch("backend.src.agent.tools.openai.OpenAI")
@patch.dict(os.environ, {"QWEN_API_KEY": "test_key"})
def test_qwen3_coder_tool_api_error(mock_openai):
    """
    Tests the qwen3_coder_tool for a failed API call.
    """
    # Arrange
    mock_client = MagicMock()
    mock_openai.return_value = mock_client
    mock_client.chat.completions.create.side_effect = Exception("API Error")

    # Act
    result = qwen3_coder_tool("test query")

    # Assert
    assert "# Error calling Qwen3 Coder API: API Error" in result

@patch("backend.src.agent.tools.openai.OpenAI")
@patch.dict(os.environ, {"QWEN_API_KEY": "test_key"})
def test_qwen3_coder_tool_cleanup(mock_openai):
    """
    Tests the qwen3_coder_tool's code cleanup logic.
    """
    # Arrange
    mock_client = MagicMock()
    mock_openai.return_value = mock_client
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "```python\nprint('Hello, World!')\n```"
    mock_client.chat.completions.create.return_value = mock_response

    # Act
    result = qwen3_coder_tool("test query")

    # Assert
    assert result == "print('Hello, World!')"
