from langchain_core.tools import tool
from specialists.research_agent.graph import graph as research_graph
from specialists.coder_agent import coder_chain
from langchain_core.messages import HumanMessage

@tool
def research_tool(query: str) -> str:
    """Use this tool to conduct research on a given topic."""
    # The research agent is a separate graph that streams its results.
    # We invoke it and return the final state.
    output = research_graph.invoke({"messages": [HumanMessage(content=query)]})
    return output.get("messages")[-1].content

@tool
def qwen3_coder_tool(language: str, prompt: str) -> str:
    """
    Use this tool for coding tasks. It takes a programming language and a prompt describing the desired code,
    invokes the specialist Qwen3 coder agent, and returns the generated code.
    """
    print(f"--- Invoking specialist coder agent for language '{language}' with prompt: {prompt} ---")
    try:
        # Invoke the dedicated coder chain with the provided inputs
        result = coder_chain.invoke({
            "language": language,
            "prompt": prompt
        })
        return result
    except Exception as e:
        return f"# Error invoking coder agent: {e}"
