import os
import pytest
from unittest.mock import patch, MagicMock
from langchain_core.messages import AIMessage, HumanMessage, ToolCall

# Since the llm is initialized inside the node, we need to patch it there.
# We still need to patch the GEMINI_API_KEY for the specialist agent import.
with patch.dict(os.environ, {"GEMINI_API_KEY": "test_key"}), \
     patch("backend.src.specialists.research_agent.graph.Client"):
    from backend.src.agent.graph import orchestrator_node, router
    from backend.src.agent.state import AgentState

@patch("backend.src.agent.graph.ChatGoogleGenerativeAI")
def test_orchestrator_node(mock_chat_google_genai):
    """
    Tests the orchestrator_node function to ensure it correctly calls the language model.
    """
    # Arrange
    mock_llm = MagicMock()
    mock_llm_with_tools = MagicMock()
    mock_chat_google_genai.return_value = mock_llm
    mock_llm.bind_tools.return_value = mock_llm_with_tools

    mock_response = AIMessage(content="LLM response")
    mock_llm_with_tools.invoke.return_value = mock_response

    sample_state = AgentState(messages=[HumanMessage(content="test message")])

    # Act
    result = orchestrator_node(sample_state)

    # Assert
    assert "messages" in result
    assert result["messages"] == [mock_response]
    mock_chat_google_genai.assert_called_once_with(model="gemini-1.5-pro-latest", temperature=0)
    mock_llm.bind_tools.assert_called_once()
    mock_llm_with_tools.invoke.assert_called_once_with(sample_state["messages"][-1])

def test_router_with_tool_calls():
    """
    Tests the router function when the last message has tool calls.
    """
    # Arrange
    sample_state = AgentState(messages=[AIMessage(content="", tool_calls=[ToolCall(name="test_tool", args={}, id="1")])])

    # Act
    result = router(sample_state)

    # Assert
    assert result == "tools"

def test_router_without_tool_calls():
    """
    Tests the router function when the last message does not have tool calls.
    """
    # Arrange
    sample_state = AgentState(messages=[AIMessage(content="Final answer")])

    # Act
    result = router(sample_state)

    # Assert
    assert result == "__end__"
