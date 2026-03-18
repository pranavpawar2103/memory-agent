from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from core.config import LLM_MODEL
from core.state import AgentState
from memory.long_term import get_memories, save_memory
from memory.session import get_session, update_session

llm = ChatOpenAI(model=LLM_MODEL)

def planner_node(state: AgentState) -> AgentState:
    user_message = state["messages"][-1].content
    user_id = state["user_id"]
    session_id = state["session_id"]

    memories = get_memories(user_id)
    session_history = get_session(session_id)

    system_prompt = (
        "You are a planning agent controlling an AI system with tools. "
        "Break the user's request into a maximum of 4 high-level steps. "
        "Do NOT include steps like 'open a browser' or 'navigate to a website'. "
        "For file write tasks, use a SINGLE step like: 'Write the content X to file Y.' "
        "Do not split into open/write/save steps. "
        "Return ONLY a numbered list, one step per line, no sub-bullets."
    )

    if memories:
        system_prompt += f"\n\nWhat you know about this user:\n{memories}"

    if session_history:
        recent = session_history[-3:]
        history_text = "\n".join(f"{m['role']}: {m['content']}" for m in recent)
        system_prompt += f"\n\nRecent conversation:\n{history_text}"

    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_message)
    ])

    steps = [
        line.strip()
        for line in response.content.strip().split("\n")
        if line.strip()
    ]

    save_memory(user_id, f"User requested: {user_message}")
    update_session(session_id, "user", user_message)

    print(f"\n[Planner] Memory loaded for user '{user_id}'")
    print(f"[Planner] Generated {len(steps)} steps:")
    for s in steps:
        print(f"  {s}")

    return {**state, "plan": steps, "current_step": 0}