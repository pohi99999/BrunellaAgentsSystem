import os
import sys
import pytest
from unittest.mock import patch, MagicMock
from langchain_core.messages import AIMessage, HumanMessage

# Ensure we can import from the backend/src module directly
CURRENT_DIR = os.path.dirname(__file__)
BACKEND_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "../../.."))
if BACKEND_ROOT not in sys.path:
    sys.path.insert(0, BACKEND_ROOT)

from src.specialists.research_agent.graph import (
    generate_query,
    continue_to_web_research,
    web_research,
    reflection,
    evaluate_research,
    finalize_answer,
)
from src.specialists.research_agent.state import (
    OverallState,
    QueryGenerationState,
    ReflectionState,
    WebSearchState,
)
from src.specialists.research_agent.configuration import Configuration

@pytest.fixture
def config():
    return Configuration(
        query_generator_model="gemini-1.5-pro-latest",
        reflection_model="gemini-1.5-pro-latest",
        answer_model="gemini-1.5-pro-latest",
        number_of_initial_queries=1,
        max_research_loops=1,
    )

@patch('src.specialists.research_agent.graph.ChatGoogleGenerativeAI')
def test_generate_query(mock_chat_google, config):
    """Tests the generate_query node."""
    # Arrange
    mock_llm = MagicMock()
    mock_chat_google.return_value.with_structured_output.return_value = mock_llm
    mock_llm.invoke.return_value = MagicMock(query=["test query"])
    state = OverallState(messages=[HumanMessage(content="test message")])

    # Act
    result = generate_query(state, config)

    # Assert
    assert result == {"search_query": ["test query"]}

def test_continue_to_web_research():
    """Tests the continue_to_web_research node."""
    # Arrange
    state = QueryGenerationState(search_query=["query1", "query2"])

    # Act
    result = continue_to_web_research(state)

    # Assert
    assert len(result) == 2
    assert result[0].node == "web_research"
    assert result[0].arg == {"search_query": "query1", "id": 0}

@patch('src.specialists.research_agent.graph.Client')
@patch('src.specialists.research_agent.graph.resolve_urls')
@patch('src.specialists.research_agent.graph.get_citations')
@patch('src.specialists.research_agent.graph.insert_citation_markers')
def test_web_research(mock_insert_citation_markers, mock_get_citations, mock_resolve_urls, mock_client, config):
    """Tests the web_research node."""
    # Arrange
    mock_response = MagicMock()
    mock_client.return_value.models.generate_content.return_value = mock_response
    mock_resolve_urls.return_value = []
    mock_get_citations.return_value = []
    mock_insert_citation_markers.return_value = "modified text"
    state = WebSearchState(search_query="test query", id=1)

    # Act
    with patch('src.specialists.research_agent.graph.genai_client', mock_client):
        result = web_research(state, config)

    # Assert
    assert result['web_research_result'] == ['modified text']

@patch('src.specialists.research_agent.graph.ChatGoogleGenerativeAI')
def test_reflection(mock_chat_google, config):
    """Tests the reflection node."""
    # Arrange
    mock_llm = MagicMock()
    mock_chat_google.return_value.with_structured_output.return_value = mock_llm
    mock_llm.invoke.return_value = MagicMock(is_sufficient=True, knowledge_gap="", follow_up_queries=[])
    state = OverallState(messages=[HumanMessage(content="test message")], web_research_result=["summary"], search_query=["test query"])

    # Act
    result = reflection(state, config)

    # Assert
    assert result['is_sufficient'] is True

def test_evaluate_research_sufficient(config):
    """Tests the evaluate_research node when research is sufficient."""
    # Arrange
    state = ReflectionState(is_sufficient=True, research_loop_count=1)

    # Act
    result = evaluate_research(state, config)

    # Assert
    assert result == "finalize_answer"

def test_evaluate_research_insufficient(config):
    """Tests the evaluate_research node when research is insufficient."""
    # Arrange
    state = ReflectionState(is_sufficient=False, research_loop_count=0, follow_up_queries=["q1"], number_of_ran_queries=1)

    # Act
    result = evaluate_research(state, config)

    # Assert
    assert len(result) == 1
    assert result[0].node == "web_research"

@patch('src.specialists.research_agent.graph.ChatGoogleGenerativeAI')
def test_finalize_answer(mock_chat_google, config):
    """Tests the finalize_answer node."""
    # Arrange
    mock_llm = MagicMock()
    mock_chat_google.return_value = mock_llm
    mock_llm.invoke.return_value = AIMessage(content="final answer")
    state = OverallState(messages=[HumanMessage(content="test")], web_research_result=["summary"], sources_gathered=[])

    # Act
    result = finalize_answer(state, config)

    # Assert
    assert result['messages'][-1].content == "final answer"
