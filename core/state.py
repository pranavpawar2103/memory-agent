from typing import TypedDict, Annotated, List
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    plan: List[str]
    current_step: int
    tool_results: List[dict]
    critic_feedback: str
    retry_count: int 
    user_id: str
    session_id: str