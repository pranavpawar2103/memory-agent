import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import chainlit as cl
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from graph.workflow import build_graph
from core.config import LLM_MODEL

graph = build_graph()
llm = ChatOpenAI(model=LLM_MODEL)

DEFAULT_USER_ID = "pranav"

@cl.on_chat_start
async def on_start():
    cl.user_session.set("session_id", cl.user_session.get("id"))
    cl.user_session.set("user_id", DEFAULT_USER_ID)
    await cl.Message(content="Hi! I'm your AI agent with memory. How can I help?").send()

@cl.on_message
async def on_message(message: cl.Message):
    session_id = cl.user_session.get("session_id")
    user_id = cl.user_session.get("user_id", DEFAULT_USER_ID)

    thinking = cl.Step(name="Agent thinking...", type="run")
    await thinking.send()

    initial_state = {
        "messages": [HumanMessage(content=message.content)],
        "plan": [],
        "current_step": 0,
        "tool_results": [],
        "critic_feedback": "",
        "retry_count": 0,
        "user_id": user_id,
        "session_id": session_id
    }

    result = graph.invoke(initial_state)
    await thinking.remove()

    # Show plan
    plan = result.get("plan", [])
    if plan:
        plan_text = "\n".join(f"{s}" for s in plan)
        await cl.Message(content=f"**Plan:**\n{plan_text}").send()

    # Build clean final response
    tool_results = result.get("tool_results", [])
    summary_prompt = (
        "Based on these task results, write a clean concise response for the user. "
        "No step numbers, no markdown headers, just a natural helpful answer.\n\n"
    )
    for r in tool_results:
        summary_prompt += f"Step: {r['step']}\nOutput: {r['output'][:400]}\n\n"

    final_response = llm.invoke([{"role": "user", "content": summary_prompt}])
    await cl.Message(content=final_response.content).send()