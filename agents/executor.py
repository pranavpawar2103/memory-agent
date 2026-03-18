from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from core.config import LLM_MODEL
from core.state import AgentState
from tools.search import web_search
from tools.code_exec import run_code
from tools.calendar import list_events, create_event
from tools.file_io import read_file, write_file, list_files

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
            "Reply with exactly one word: SEARCH, CODE, CALENDAR, FILE, or LLM.\n"
            "Use FILE if the step mentions reading, writing, listing, or saving a file. "
            "Use SEARCH for web lookups. Use CODE for running Python. "
            "Use CALENDAR for scheduling. Use LLM for everything else."
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
                "Based on this task, reply with LIST if checking events, "
                "or CREATE:<title>|<date YYYY-MM-DD>|<time HH:MM>|<email1,email2> if creating. "
                "Leave emails empty if none mentioned."
            )),
            HumanMessage(content=current_step)
        ])
        action_text = action.content.strip()
        if action_text.startswith("CREATE:"):
            parts = action_text.replace("CREATE:", "").split("|")
            title = parts[0].strip()
            date = parts[1].strip()
            time = parts[2].strip() if len(parts) > 2 else "10:00"
            emails = [e.strip() for e in parts[3].split(",")] if len(parts) > 3 and parts[3].strip() else []
            tool_output = create_event(title, date, time, attendees=emails)
        else:
            tool_output = list_events()

    elif tool == "FILE":
        action = llm.invoke([
            SystemMessage(content=(
                "Reply with exactly one of these formats:\n"
                "READ:<path>\n"
                "WRITE:<path>|<content>\n"
                "LIST:<directory>\n\n"
                "IMPORTANT: Use the ACTUAL filename and content from the task. "
                "Never use placeholders like <path> or <file_path>. "
                "If the filename is test.txt, write READ:test.txt not READ:<path>."
            )),
            HumanMessage(content=current_step)
        ])
        action_text = action.content.strip()
        print(f"[Executor] File action: {action_text}")
        if action_text.startswith("READ:"):
            path = action_text.replace("READ:", "").strip()
            tool_output = read_file(path)
        elif action_text.startswith("WRITE:"):
            parts = action_text.replace("WRITE:", "").split("|", 1)
            if len(parts) == 2:
                tool_output = write_file(parts[0].strip(), parts[1].strip())
            else:
                tool_output = "Invalid format."
        elif action_text.startswith("LIST:"):
            directory = action_text.replace("LIST:", "").strip() or "."
            tool_output = list_files(directory)
        else:
            tool_output = "Could not parse file action."

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