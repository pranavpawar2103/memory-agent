from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from core.config import LLM_MODEL
from core.state import AgentState
from tools.search import web_search
from tools.code_exec import run_code
from tools.calendar import list_events, create_event

llm = ChatOpenAI(model=LLM_MODEL)

def executor_node(state: AgentState) -> AgentState:
    plan = state["plan"]
    step_idx = state["current_step"]

    if step_idx >= len(plan):
        return state

    current_step = plan[step_idx]
    print(f"\n[Executor] Running step {step_idx + 1}: {current_step}")

    tool_decision = llm.invoke([
        SystemMessage(content=(
            "You decide which tool to use for a task step. "
            "Reply with exactly one word: SEARCH, CODE, CALENDAR, or LLM.\n"
            "Use CALENDAR for anything involving scheduling, events, or calendar."
        )),
        HumanMessage(content=current_step)
    ])

    tool = tool_decision.content.strip().upper()
    print(f"[Executor] Tool selected: {tool}")

    if tool == "SEARCH":
        tool_output = web_search(current_step)

    elif tool == "CODE":
        code_response = llm.invoke([
            SystemMessage(content="Write clean Python code to complete this task. Return only the code, no explanation."),
            HumanMessage(content=current_step)
        ])
        code = code_response.content.strip().removeprefix("```python").removesuffix("```").strip()
        print(f"[Executor] Running code:\n{code}")
        tool_output = run_code(code)

    elif tool == "CALENDAR":
        action = llm.invoke([
            SystemMessage(content=(
                "Based on this task, reply with LIST if it's checking/listing events, "
                "or CREATE:<title>|<date YYYY-MM-DD>|<time HH:MM> if creating an event."
            )),
            HumanMessage(content=current_step)
        ])
        action_text = action.content.strip()
        if action_text.startswith("CREATE:"):
            parts = action_text.replace("CREATE:", "").split("|")
            if len(parts) >= 2:
                title = parts[0].strip()
                date = parts[1].strip()
                time = parts[2].strip() if len(parts) > 2 else "10:00"
                tool_output = create_event(title, date, time)
            else:
                tool_output = "Could not parse event details."
        else:
            tool_output = list_events()

    else:
        response = llm.invoke([
            SystemMessage(content="You are an execution agent. Complete the given task step thoroughly."),
            HumanMessage(content=current_step)
        ])
        tool_output = response.content

    print(f"[Executor] Output: {tool_output[:150]}...")

    result = {
        "step": current_step,
        "tool_used": tool,
        "output": tool_output,
        "step_index": step_idx
    }

    return {
        **state,
        "tool_results": state["tool_results"] + [result],
        "current_step": step_idx + 1
    }