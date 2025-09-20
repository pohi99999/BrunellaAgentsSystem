import os
import pytest
from unittest.mock import patch, MagicMock
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import HumanMessage

@patch.dict(os.environ, {"GEMINI_API_KEY": "test_key"})
@patch("backend.src.specialists.research_agent.graph.ChatGoogleGenerativeAI")
@patch("backend.src.specialists.research_agent.graph.Client")
def test_generate_query(mock_genai_client, mock_chat_google_genai):
    """
    Tests the generate_query function to ensure it generates search queries correctly.
    """
    from backend.src.specialists.research_agent.graph import generate_query
    from backend.src.specialists.research_agent.tools_and_schemas import SearchQueryList

    # Arrange
    # Mock the language model and its response
    mock_llm = MagicMock()
    mock_structured_llm = MagicMock()
    mock_chat_google_genai.return_value = mock_llm
    mock_llm.with_structured_output.return_value = mock_structured_llm

    expected_queries = ["what is the latest AI news?", "new AI models in 2025"]
    mock_structured_llm.invoke.return_value = SearchQueryList(
        query=expected_queries,
        rationale="To get the latest news and updates on AI models."
    )

    # Create a sample state and config
    sample_state = {
        "messages": [HumanMessage(content="What's new in AI?")],
    }
    sample_config = RunnableConfig(
        configurable={
            "query_generator_model": "gemini-1.5-flash",
            "number_of_initial_queries": 2,
        }
    )

    # Act
    result = generate_query(sample_state, sample_config)

    # Assert
    # Check that the result contains the expected search queries
    assert "search_query" in result
    assert result["search_query"] == expected_queries

    # Check that the mock was called correctly
    mock_chat_google_genai.assert_called_once()
    mock_llm.with_structured_output.assert_called_once_with(SearchQueryList)
    mock_structured_llm.invoke.assert_called_once()

@patch.dict(os.environ, {"GEMINI_API_KEY": "test_key"})
@patch("backend.src.specialists.research_agent.graph.resolve_urls", return_value=[{"short_url": "http://short.url/1", "value": "http://original.url/1"}])
@patch("backend.src.specialists.research_agent.graph.get_citations", return_value=[{"segments": [{"value": "citation1"}]}])
@patch("backend.src.specialists.research_agent.graph.insert_citation_markers", return_value="Modified text with citations")
@patch("backend.src.specialists.research_agent.graph.genai_client")
def test_web_research(mock_genai_client, mock_insert_citation_markers, mock_get_citations, mock_resolve_urls):
    """
    Tests the web_research function to ensure it performs web research correctly.
    """
    from backend.src.specialists.research_agent.graph import web_research

    # Arrange
    mock_response = MagicMock()
    mock_response.text = "Original text"
    mock_response.candidates[0].grounding_metadata.grounding_chunks = ["chunk1"]
    mock_genai_client.models.generate_content.return_value = mock_response

    sample_state = {
        "search_query": "test query",
        "id": 1
    }
    sample_config = RunnableConfig(
        configurable={
            "query_generator_model": "gemini-1.5-flash",
        }
    )

    # Act
    result = web_research(sample_state, sample_config)

    # Assert
    assert "sources_gathered" in result
    assert "web_research_result" in result
    assert result["sources_gathered"] == [{"value": "citation1"}]
    assert result["web_research_result"] == ["Modified text with citations"]

    mock_genai_client.models.generate_content.assert_called_once()
    mock_resolve_urls.assert_called_once_with(["chunk1"], 1)
    mock_get_citations.assert_called_once()
    mock_insert_citation_markers.assert_called_once_with("Original text", [{"segments": [{"value": "citation1"}]}])

@patch.dict(os.environ, {"GEMINI_API_KEY": "test_key"})
@patch("backend.src.specialists.research_agent.graph.ChatGoogleGenerativeAI")
@patch("backend.src.specialists.research_agent.graph.Client")
def test_reflection(mock_genai_client, mock_chat_google_genai):
    """
    Tests the reflection function to ensure it correctly identifies knowledge gaps and generates follow-up queries.
    """
    from backend.src.specialists.research_agent.graph import reflection
    from backend.src.specialists.research_agent.tools_and_schemas import Reflection

    # Arrange
    mock_llm = MagicMock()
    mock_structured_llm = MagicMock()
    mock_chat_google_genai.return_value = mock_llm
    mock_llm.with_structured_output.return_value = mock_structured_llm

    expected_reflection = Reflection(
        is_sufficient=False,
        knowledge_gap="Need more details on topic X.",
        follow_up_queries=["details on topic X"]
    )
    mock_structured_llm.invoke.return_value = expected_reflection

    sample_state = {
        "messages": [HumanMessage(content="What about topic X?")],
        "web_research_result": ["Summary of topic X."],
        "search_query": ["topic X"],
    }
    sample_config = RunnableConfig(
        configurable={
            "reflection_model": "gemini-1.5-flash",
        }
    )

    # Act
    result = reflection(sample_state, sample_config)

    # Assert
    assert result["is_sufficient"] is False
    assert result["knowledge_gap"] == "Need more details on topic X."
    assert result["follow_up_queries"] == ["details on topic X"]
    assert result["research_loop_count"] == 1
    assert result["number_of_ran_queries"] == 1

    mock_chat_google_genai.assert_called_once()
    mock_llm.with_structured_output.assert_called_once_with(Reflection)
    mock_structured_llm.invoke.assert_called_once()

@patch.dict(os.environ, {"GEMINI_API_KEY": "test_key"})
@patch("backend.src.specialists.research_agent.graph.ChatGoogleGenerativeAI")
@patch("backend.src.specialists.research_agent.graph.Client")
def test_finalize_answer(mock_genai_client, mock_chat_google_genai):
    """
    Tests the finalize_answer function to ensure it generates a final answer correctly.
    """
    from backend.src.specialists.research_agent.graph import finalize_answer
    from langchain_core.messages import AIMessage

    # Arrange
    mock_llm = MagicMock()
    mock_chat_google_genai.return_value = mock_llm
    mock_llm.invoke.return_value = AIMessage(content="Final answer with [http://short.url/1](http://short.url/1).")

    sample_state = {
        "messages": [HumanMessage(content="What about topic X?")],
        "web_research_result": ["Summary of topic X."],
        "sources_gathered": [{"short_url": "[http://short.url/1](http://short.url/1)", "value": "http://original.url/1"}]
    }
    sample_config = RunnableConfig(
        configurable={
            "answer_model": "gemini-1.5-flash",
        }
    )

    # Act
    result = finalize_answer(sample_state, sample_config)

    # Assert
    assert "messages" in result
    assert isinstance(result["messages"][0], AIMessage)
    assert "http://original.url/1" in result["messages"][0].content
    assert "sources_gathered" in result
    assert result["sources_gathered"] == [{"short_url": "[http://short.url/1](http://short.url/1)", "value": "http://original.url/1"}]

    mock_chat_google_genai.assert_called_once()
    mock_llm.invoke.assert_called_once()
