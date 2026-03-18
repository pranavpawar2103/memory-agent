from langchain_openai import ChatOpenAI
from core.config import LLM_MODEL
from core.state import AgentState

llm = ChatOpenAI(model=LLM_MODEL)

def critic_node(state: AgentState) -> AgentState:
    if not state["tool_results"]:
        return {**state, "critic_feedback": "no results to review", "retry_count": 0}

    last_result = state["tool_results"][-1]

    response = llm.invoke([
        {"role": "system", "content": (
            "You are a critic agent. Reply with 'PASS' if the output is "
            "reasonable, or 'RETRY: <reason>' only if it is completely wrong. "
            "Be lenient — partial answers are acceptable."
        )},
        {"role": "user", "content": (
            f"Step: {last_result['step']}\n"
            f"Output: {last_result['output']}"
        )}
    ])

    feedback = response.content.strip()
    retry_count = state.get("retry_count", 0)

    if feedback.startswith("RETRY"):
        retry_count += 1
    else:
        retry_count = 0

    print(f"\n[Critic] Verdict: {feedback[:80]}")
    return {**state, "critic_feedback": feedback, "retry_count": retry_count}