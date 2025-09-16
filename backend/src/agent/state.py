from typing import Annotated, Literal

from langchain_core.messages import AnyMessage
from typing_extensions import TypedDict


class AgentState(TypedDict):
    """
    The state of the orchestrator agent.
    """

    messages: Annotated[list[AnyMessage], lambda x, y: x + y]
    