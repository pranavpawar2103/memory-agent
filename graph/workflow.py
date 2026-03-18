from langgraph.graph import StateGraph, END
from core.state import AgentState
from agents.planner import planner_node
from agents.executor import executor_node
from agents.critic import critic_node

def should_continue(state: AgentState) -> str:
    feedback = state.get("critic_feedback", "")
    current_step = state.get("current_step", 0)
    plan_length = len(state.get("plan", []))
    retry_count = state.get("retry_count", 0)

    if feedback.startswith("RETRY") and retry_count < 2:
        return "retry"
    if current_step < plan_length:
        return "continue"
    return "done"

def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("planner", planner_node)
    graph.add_node("executor", executor_node)
    graph.add_node("critic", critic_node)

    graph.set_entry_point("planner")
    graph.add_edge("planner", "executor")
    graph.add_edge("executor", "critic")

    graph.add_conditional_edges("critic", should_continue, {
        "retry": "executor",
        "continue": "executor",
        "done": END
    })

    return graph.compile()