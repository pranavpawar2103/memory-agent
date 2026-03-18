from graph.workflow import build_graph
from langchain_core.messages import HumanMessage

def run(task: str, user_id: str = "test_user", session_id: str = "session_001"):
    graph = build_graph()

    initial_state = {
        "messages": [HumanMessage(content=task)],
        "plan": [],
        "current_step": 0,
        "tool_results": [],
        "critic_feedback": "",
        "retry_count": 0,
        "user_id": user_id,
        "session_id": session_id
    }

    print(f"\n=== Running task: {task} ===")
    result = graph.invoke(initial_state)

    print("\n=== Final Results ===")
    for r in result["tool_results"]:
        print(f"\nStep: {r['step']}")
        print(f"Output: {r['output'][:200]}...")

if __name__ == "__main__":
    # First run — agent learns about the user
    run(
        task="Search the web for the top 3 AI trends in 2025",
        user_id="pranav",
        session_id="session_001"
    )

    # Second run — agent should remember pranav
    run(
        task="Summarize what we just discussed",
        user_id="pranav",
        session_id="session_001"
    )