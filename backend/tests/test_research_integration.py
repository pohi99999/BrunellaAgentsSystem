import os
from unittest.mock import patch, MagicMock

import pytest
from langchain_core.messages import HumanMessage, AIMessage

from src.specialists.research_agent.graph import graph
from src.specialists.research_agent.state import OverallState


@pytest.fixture
def mock_gemini_api_key():
    """Mock the Gemini API key for testing."""
    with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"}):
        yield


@pytest.fixture
def mock_genai_client():
    """Mock the Google GenAI Client for search."""
    with patch("src.specialists.research_agent.graph._get_genai_client") as mock_client:
        mock_instance = MagicMock()
        mock_client.return_value = mock_instance
        
        # Mock search response with grounding metadata
        mock_search_result = MagicMock()
        mock_search_result.text = "Python is a high-level programming language known for its simplicity."
        mock_search_result.grounding_metadata = MagicMock()
        mock_search_result.grounding_metadata.grounding_chunks = [
            MagicMock(
                web=MagicMock(
                    uri="https://python.org",
                    title="Python Official Site"
                )
            )
        ]
        mock_instance.models.generate_content.return_value = mock_search_result
        
        yield mock_instance


@pytest.fixture
def mock_chat_google():
    """Mock ChatGoogleGenerativeAI for query generation, reflection, and answer."""
    with patch("src.specialists.research_agent.graph.ChatGoogleGenerativeAI") as mock_chat:
        # Create different mocks for different stages
        mock_llm = MagicMock()
        mock_chat.return_value = mock_llm
        
        # Mock structured output for query generation
        mock_query_output = MagicMock()
        mock_query_output.queries = ["what is python programming"]
        
        # Mock structured output for reflection
        mock_reflection_output = MagicMock()
        mock_reflection_output.is_sufficient = True
        mock_reflection_output.knowledge_gap = ""
        mock_reflection_output.follow_up_queries = []
        
        # Set up the mock to return appropriate values
        def with_structured_output_side_effect(schema):
            mock_structured = MagicMock()
            if schema.__name__ == "SearchQueryList":
                mock_structured.invoke.return_value = mock_query_output
            elif schema.__name__ == "Reflection":
                mock_structured.invoke.return_value = mock_reflection_output
            return mock_structured
        
        mock_llm.with_structured_output.side_effect = with_structured_output_side_effect
        
        # Mock invoke for final answer
        mock_answer = MagicMock()
        mock_answer.content = "Python is a programming language. [1]"
        mock_llm.invoke.return_value = mock_answer
        
        yield mock_chat


def test_research_agent_full_cycle(mock_gemini_api_key, mock_genai_client, mock_chat_google):
    """Test the complete research agent graph execution."""
    # Prepare initial state
    initial_state: OverallState = {
        "messages": [HumanMessage(content="What is Python programming?")],
        "web_research_result": [],
        "sources_gathered": [],
        "search_query": [],
        "initial_search_query_count": 1,
        "max_research_loops": 1,
        "research_loop_count": 0,
        "reasoning_model": "gemini-2.0-flash-exp",
    }
    
    # Invoke the graph
    config = {
        "configurable": {
            "initial_search_query_count": 1,
            "max_research_loops": 1,
        }
    }
    
    result = graph.invoke(initial_state, config)
    
    # Verify the graph executed successfully
    assert "messages" in result
    assert len(result["messages"]) > 0
    
    # Verify the final message is an AIMessage
    final_message = result["messages"][-1]
    assert isinstance(final_message, AIMessage)
    assert len(final_message.content) > 0
    
    # Verify state changes
    assert result["research_loop_count"] > 0
    assert len(result["search_query"]) > 0


def test_research_agent_with_max_loops(mock_gemini_api_key, mock_genai_client, mock_chat_google):
    """Test that the research agent respects max_research_loops configuration."""
    # Mock reflection to always return insufficient
    mock_reflection_insufficient = MagicMock()
    mock_reflection_insufficient.is_sufficient = False
    mock_reflection_insufficient.knowledge_gap = "Need more info"
    mock_reflection_insufficient.follow_up_queries = ["follow up query"]
    
    with patch("src.specialists.research_agent.graph.ChatGoogleGenerativeAI") as mock_chat:
        mock_llm = MagicMock()
        mock_chat.return_value = mock_llm
        
        def with_structured_output_side_effect(schema):
            mock_structured = MagicMock()
            if schema.__name__ == "SearchQueryList":
                mock_query = MagicMock()
                mock_query.queries = ["test query"]
                mock_structured.invoke.return_value = mock_query
            elif schema.__name__ == "Reflection":
                mock_structured.invoke.return_value = mock_reflection_insufficient
            return mock_structured
        
        mock_llm.with_structured_output.side_effect = with_structured_output_side_effect
        mock_answer = MagicMock()
        mock_answer.content = "Final answer"
        mock_llm.invoke.return_value = mock_answer
        
        initial_state: OverallState = {
            "messages": [HumanMessage(content="What is AI?")],
            "web_research_result": [],
            "sources_gathered": [],
            "search_query": [],
            "initial_search_query_count": 1,
            "max_research_loops": 2,
            "research_loop_count": 0,
            "reasoning_model": "gemini-2.0-flash-exp",
        }
        
        config = {
            "configurable": {
                "initial_search_query_count": 1,
                "max_research_loops": 2,  # Set max loops to 2
            }
        }
        
        result = graph.invoke(initial_state, config)
        
        # Verify the graph stopped after max loops
        assert result["research_loop_count"] <= 2


def test_research_agent_empty_message():
    """Test that the research agent handles empty messages gracefully."""
    initial_state: OverallState = {
        "messages": [],
        "web_research_result": [],
        "sources_gathered": [],
        "search_query": [],
        "initial_search_query_count": 1,
        "max_research_loops": 1,
        "research_loop_count": 0,
        "reasoning_model": "gemini-2.0-flash-exp",
    }
    
    # This should raise an error or handle gracefully
    with pytest.raises(Exception):
        graph.invoke(initial_state)
