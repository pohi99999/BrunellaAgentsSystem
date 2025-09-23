import os
import sys
import pytest
from unittest.mock import patch, MagicMock
from langchain_core.messages import AIMessage, HumanMessage, ToolCall

# Ensure we can import from the backend/src module directly
CURRENT_DIR = os.path.dirname(__file__)
BACKEND_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "../.."))
if BACKEND_ROOT not in sys.path:
    sys.path.insert(0, BACKEND_ROOT)

from src.agent.state import AgentState

# Since the graph is initialized at module level, we need to patch the dependencies before importing the graph
@pytest.fixture(autouse=True)
def mock_dependencies():
    with patch('src.agent.graph.ChatGoogleGenerativeAI') as mock_chat_google, \
         patch('src.agent.tools.research_graph'), \
         patch('src.agent.tools.coder_chain'), \
         patch('langgraph.prebuilt.ToolNode') as mock_tool_node:
        # you can configure your mocks here if needed
        yield mock_chat_google, mock_tool_node


@pytest.fixture
def mock_llm_with_tools(mock_dependencies):
    """Fixture to mock the llm_with_tools object."""
    # The llm_with_tools is derived from the mocked ChatGoogleGenerativeAI, so we can just use the mock
    mock_chat_google, _ = mock_dependencies
    # let's make sure bind_tools returns a mock that has an invoke method
    mock_llm = MagicMock()
    mock_chat_google.return_value.bind_tools.return_value = mock_llm
    return mock_llm

def test_orchestrator_node(mock_llm_with_tools):
    """Tests the orchestrator_node function."""
    # Arrange
    from src.agent.graph import orchestrator_node
    mock_response = AIMessage(content="", tool_calls=[ToolCall(name="research", args={"query": "test"}, id="1")])
    mock_llm_with_tools.invoke.return_value = mock_response
    state = AgentState(messages=[HumanMessage(content="test message")])

    # Act
    result = orchestrator_node(state)

    # Assert
    mock_llm_with_tools.invoke.assert_called_once_with(state["messages"][-1])
    assert result == {"messages": [mock_response]}

def test_router_with_tool_calls():
    """Tests the router function when there are tool calls."""
    # Arrange
    from src.agent.graph import router
    state = AgentState(messages=[AIMessage(content="", tool_calls=[ToolCall(name="research", args={"query": "test"}, id="1")])])

    # Act
    result = router(state)

    # Assert
    assert result == "tools"

def test_router_without_tool_calls():
    """Tests the router function when there are no tool calls."""
    # Arrange
    from src.agent.graph import router
    state = AgentState(messages=[AIMessage(content="hello")])

    # Act
    result = router(state)

    # Assert
    assert result == "__end__"

def test_graph_integration(mock_dependencies):
    """Tests the compiled graph for a simple interaction."""
    # Arrange
    from src.agent.graph import graph
    mock_chat_google, mock_tool_node = mock_dependencies

    # Mock the LLM and its responses
    mock_llm = MagicMock()
    mock_chat_google.return_value.bind_tools.return_value = mock_llm

    tool_call = ToolCall(name="research_tool", args={"query": "test query"}, id="123")
    llm_response_with_tool = AIMessage(content="", tool_calls=[tool_call])
    final_response = AIMessage(content="LangGraph is a library for building stateful, multi-actor applications with LLMs.")
    mock_llm.invoke.side_effect = [llm_response_with_tool, final_response]

    # Mock the ToolNode
    mock_tool_node.return_value = MagicMock(return_value={"messages": [HumanMessage(content="Mocked tool output")]})

    # Act
    inputs = {"messages": [HumanMessage(content="What is langgraph?")]}
    result = graph.invoke(inputs)

    # Assert
    assert mock_llm.invoke.call_count == 2
    assert result['messages'][-1].content == final_response.content
