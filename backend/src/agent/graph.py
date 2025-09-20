
import os
from typing import Literal

from langchain_core.messages import ToolCall
from langgraph.graph import StateGraph, START
from langgraph.graph.message import AnyMessage, add_messages
from langgraph.prebuilt import ToolNode
from langchain_google_genai import ChatGoogleGenerativeAI

from .state import AgentState
from .tools import research_tool, qwen3_coder_tool

# Set up the tool-calling model
llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro-latest", temperature=0)
tools = [research_tool, qwen3_coder_tool]
llm_with_tools = llm.bind_tools(tools)

# Define the orchestrator node
def orchestrator_node(state: AgentState):
    """The main node that decides which tool to call based on the user's request."""
    # Get the latest message
    message = state["messages"][-1]
    # Call the model with the message and tools
    response = llm_with_tools.invoke(message)
    return {"messages": [response]}

# Define the router
def router(state: AgentState) -> Literal["__end__", "tools"]:
    """Routes the conversation to the tool node or ends the conversation."""
    last_message = state["messages"][-1]
    if not last_message.tool_calls:
        return "__end__"
    return "tools"

# Create the graph
builder = StateGraph(AgentState)

# Add the nodes
builder.add_node("orchestrator", orchestrator_node)
builder.add_node("tools", ToolNode(tools))

# Set the entrypoint
builder.add_edge(START, "orchestrator")

# Add the conditional router
builder.add_conditional_edges(
    "orchestrator",
    router,
)

# Add the edge from the tool node back to the orchestrator
builder.add_edge("tools", "orchestrator")

# Compile the graph
graph = builder.compile()
