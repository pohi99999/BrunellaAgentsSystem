"""
Unit tests for the orchestrator agent functionality.
"""
import pytest
from unittest.mock import Mock, patch
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

from agent.graph import orchestrator_node, router
from agent.state import AgentState


class TestOrchestratorNode:
    """Tests for the orchestrator node."""

    @patch("agent.graph.llm")
    def test_orchestrator_routes_to_research_tool(self, mock_llm):
        """Test that orchestrator correctly routes research queries to research_tool."""
        # Setup mock LLM response with tool call
        mock_response = AIMessage(
            content="",
            tool_calls=[
                {
                    "name": "research_tool",
                    "args": {"query": "What are the latest AI trends?"},
                    "id": "call_123",
                }
            ],
        )
        mock_llm.invoke.return_value = mock_response

        # Test input state
        state: AgentState = {
            "messages": [HumanMessage(content="Research AI trends")]
        }

        # Execute
        result = orchestrator_node(state)

        # Verify
        assert len(result["messages"]) == 1
        assert isinstance(result["messages"][0], AIMessage)
        assert len(result["messages"][0].tool_calls) == 1
        assert result["messages"][0].tool_calls[0]["name"] == "research_tool"

    @patch("agent.graph.llm")
    def test_orchestrator_routes_to_coder_tool(self, mock_llm):
        """Test that orchestrator correctly routes coding queries to qwen3_coder_tool."""
        # Setup mock LLM response
        mock_response = AIMessage(
            content="",
            tool_calls=[
                {
                    "name": "qwen3_coder_tool",
                    "args": {"language": "python", "prompt": "Create a factorial function"},
                    "id": "call_456",
                }
            ],
        )
        mock_llm.invoke.return_value = mock_response

        # Test input
        state: AgentState = {
            "messages": [HumanMessage(content="Write a Python factorial function")]
        }

        # Execute
        result = orchestrator_node(state)

        # Verify
        assert len(result["messages"]) == 1
        assert result["messages"][0].tool_calls[0]["name"] == "qwen3_coder_tool"
        assert result["messages"][0].tool_calls[0]["args"]["language"] == "python"

    def test_orchestrator_handles_empty_messages(self):
        """Test that orchestrator handles empty message list gracefully."""
        state: AgentState = {"messages": []}

        with pytest.raises((IndexError, KeyError, ValueError)):
            orchestrator_node(state)


class TestRouteAfterOrchestrator:
    """Tests for routing logic after orchestrator."""

    def test_route_to_tools_when_tool_calls_exist(self):
        """Test routing to 'tools' when AI message has tool calls."""
        state: AgentState = {
            "messages": [
                AIMessage(
                    content="",
                    tool_calls=[{"name": "research_tool", "args": {}, "id": "1"}],
                )
            ]
        }

        result = router(state)
        assert result == "tools"

    def test_route_to_end_when_no_tool_calls(self):
        """Test routing to END when AI message has no tool calls."""
        state: AgentState = {
            "messages": [AIMessage(content="Here's your answer")]
        }

        result = router(state)
        assert result == "__end__"

    def test_route_handles_mixed_messages(self):
        """Test routing with mixed message types (last message wins)."""
        state: AgentState = {
            "messages": [
                HumanMessage(content="Question"),
                AIMessage(content="", tool_calls=[{"name": "test", "args": {}, "id": "1"}]),
                ToolMessage(content="Tool result", tool_call_id="1"),
                AIMessage(content="Final answer"),
            ]
        }

        result = router(state)
        assert result == "__end__"  # Last message has no tool calls


class TestOrchestratorIntegration:
    """Integration tests for orchestrator flow."""

    @patch("agent.tools.research_graph")
    @patch("agent.graph.llm")
    def test_full_research_flow(self, mock_llm, mock_research_graph):
        """Test complete flow from question to research tool invocation."""
        # Mock LLM to call research tool
        mock_llm.invoke.return_value = AIMessage(
            content="",
            tool_calls=[
                {
                    "name": "research_tool",
                    "args": {"query": "AI trends 2025"},
                    "id": "call_789",
                }
            ],
        )

        # Mock research graph response
        mock_research_graph.invoke.return_value = {
            "messages": [AIMessage(content="AI trends include: ...")]
        }

        # Initial state
        state: AgentState = {
            "messages": [HumanMessage(content="What are AI trends in 2025?")]
        }

        # Execute orchestrator
        orch_result = orchestrator_node(state)

        # Verify orchestrator output
        assert len(orch_result["messages"]) == 1
        assert orch_result["messages"][0].tool_calls[0]["name"] == "research_tool"

        # Verify routing
        route = router(orch_result)
        assert route == "tools"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
