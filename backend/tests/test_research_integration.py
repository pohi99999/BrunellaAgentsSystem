import sys
import os
import importlib
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
import pytest

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

# Import the module so we can reload it
from specialists.research_agent.graph import graph

@patch('specialists.research_agent.graph.genai_client')
def test_research_full_cycle(mock_genai_client_instance):
    """
    Test the full cycle of the research agent, from query to final answer.
    """
    # Create a mock object for the grounding chunk
    mock_chunk = MagicMock()
    mock_chunk.web.uri = "https://example.com"
    mock_chunk.web.title = "Example"

    # Mock the Google Search API client instance
    mock_genai_client_instance.models.generate_content.return_value = MagicMock(
        text="This is a mock search result.",
        candidates=[MagicMock(
            grounding_metadata=MagicMock(grounding_chunks=[mock_chunk])
        )]
    )

    # Mock the ChatGoogleGenerativeAI class
    with patch('specialists.research_agent.graph.ChatGoogleGenerativeAI') as mock_chat_model:
        # Mock the structured_llm for query generation
        mock_query_llm = MagicMock()
        mock_query_llm.with_structured_output.return_value.invoke.return_value = MagicMock(
            query=["What is the capital of France?"]
        )

        # Mock the structured_llm for reflection
        mock_reflection_llm = MagicMock()
        mock_reflection_llm.with_structured_output.return_value.invoke.return_value = MagicMock(
            is_sufficient=True,
            knowledge_gap="",
            follow_up_queries=[]
        )

        # Mock the llm for the final answer
        mock_answer_llm = MagicMock()
        mock_answer_llm.invoke.return_value = MagicMock(content="The capital of France is Paris.")

        # Set the side_effect to return the different mocked LLMs
        mock_chat_model.side_effect = [mock_query_llm, mock_reflection_llm, mock_answer_llm]

        # Define the input for the graph
        inputs = {"messages": [("user", "What is the capital of France?")]}

        # Run the graph
        result = graph.invoke(inputs)

        # Assert the final answer
        assert "The capital of France is Paris." in result['messages'][-1].content

        # Assert that the search client was called
        mock_genai_client_instance.models.generate_content.assert_called()

@patch('specialists.research_agent.graph.genai_client')
def test_research_max_loops(mock_genai_client_instance):
    """
    Test that the research agent stops after the maximum number of loops.
    """
    # Create a mock object for the grounding chunk
    mock_chunk = MagicMock()
    mock_chunk.web.uri = "https://example.com"
    mock_chunk.web.title = "Example"

    # Mock the Google Search API client instance
    mock_genai_client_instance.models.generate_content.return_value = MagicMock(
        text="This is a mock search result.",
        candidates=[MagicMock(
            grounding_metadata=MagicMock(grounding_chunks=[mock_chunk])
        )]
    )

    # Mock the ChatGoogleGenerativeAI class
    with patch('specialists.research_agent.graph.ChatGoogleGenerativeAI') as mock_chat_model:
        # Mock the structured_llm for query generation
        mock_query_llm = MagicMock()
        mock_query_llm.with_structured_output.return_value.invoke.return_value = MagicMock(
            query=["What is the capital of France?"]
        )

        # Mock the structured_llm for reflection to always be insufficient
        mock_reflection_llm = MagicMock()
        mock_reflection_llm.with_structured_output.return_value.invoke.return_value = MagicMock(
            is_sufficient=False,
            knowledge_gap="There is more to learn.",
            follow_up_queries=["What is the population of France?"]
        )

        # Mock the llm for the final answer
        mock_answer_llm = MagicMock()
        mock_answer_llm.invoke.return_value = MagicMock(content="The capital of France is Paris, and the population is 65 million.")

        # This setup will cause the reflection node to be called twice, and the answer node once.
        # So we need to provide enough mocks for the ChatGoogleGenerativeAI constructor.
        # 1st call in generate_query
        # 2nd call in reflection (loop 1)
        # 3rd call in reflection (loop 2)
        # 4th call in finalize_answer
        mock_chat_model.side_effect = [
            mock_query_llm,
            mock_reflection_llm,
            mock_reflection_llm,
            mock_answer_llm
        ]

        # Define the input for the graph
        inputs = {"messages": [("user", "What is the capital and population of France?")]}

        # Set the max_research_loops to 2
        config = {"configurable": {"max_research_loops": 2}}

        # Run the graph
        result = graph.invoke(inputs, config=config)

        # Assert the final answer
        assert "The capital of France is Paris, and the population is 65 million." in result['messages'][-1].content

        # Assert that the reflection model was invoked twice
        assert mock_reflection_llm.with_structured_output.return_value.invoke.call_count == 2
