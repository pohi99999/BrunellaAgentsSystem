import logging
from langchain_core.tools import tool
from src.specialists.research_agent.graph import graph as research_graph
from src.specialists.coder_agent import coder_chain
from langchain_core.messages import HumanMessage

logger = logging.getLogger(__name__)

@tool
def research_tool(query: str) -> str:
    """Use this tool to conduct research on a given topic."""
    try:
        # The research agent is a separate graph that streams its results.
        # We invoke it and return the final state.
        output = research_graph.invoke({"messages": [HumanMessage(content=query)]})
        messages = output.get("messages", [])
        if not messages:
            logger.warning("Research tool returned no messages for query: %s", query[:100])
            return "Research failed: No results returned."
        return messages[-1].content
    except (KeyError, IndexError) as e:
        logger.error("Research tool data structure error: %s", e)
        return f"Research failed: Invalid response format - {e}"
    except Exception as e:
        logger.exception("Research tool failed for query: %s", query[:100])
        return f"Research failed: {str(e)}"

@tool
def qwen3_coder_tool(language: str, prompt: str) -> str:
    """
    Use this tool for coding tasks. It takes a programming language and a prompt describing the desired code,
    invokes the specialist Qwen3 coder agent, and returns the generated code.
    """
    logger.info("Invoking coder agent", extra={"language": language, "prompt_length": len(prompt)})
    try:
        # Invoke the dedicated coder chain with the provided inputs
        result = coder_chain.invoke({
            "language": language,
            "prompt": prompt
        })
        return result
    except (ValueError, RuntimeError) as e:
        logger.error("Coder agent error: %s", e)
        return f"# Error invoking coder agent: {e}"
    except Exception as e:
        logger.exception("Unexpected error in coder agent")
        return f"# Critical error invoking coder agent: {e}"
