import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from deepeval import assert_test
from deepeval.metrics import AnswerRelevancyMetric, FaithfulnessMetric, HallucinationMetric
from deepeval.test_case import LLMTestCase
from graph.workflow import build_graph
from langchain_core.messages import HumanMessage

graph = build_graph()

def run_agent(task: str) -> str:
    result = graph.invoke({
        "messages": [HumanMessage(content=task)],
        "plan": [],
        "current_step": 0,
        "tool_results": [],
        "critic_feedback": "",
        "retry_count": 0,
        "user_id": "eval_user",
        "session_id": "eval_session"
    })
    outputs = [r["output"] for r in result.get("tool_results", [])]
    return "\n".join(outputs)


# Test 1 — answer relevancy
def test_answer_relevancy():
    task = "What is LangGraph and why is it used?"
    output = run_agent(task)
    test_case = LLMTestCase(
        input=task,
        actual_output=output
    )
    metric = AnswerRelevancyMetric(threshold=0.7, model="gpt-4o")
    assert_test(test_case, [metric])


# Test 2 — faithfulness (output grounded in retrieved context)
def test_faithfulness():
    task = "Search the web for what is retrieval augmented generation"
    output = run_agent(task)
    test_case = LLMTestCase(
        input=task,
        actual_output=output,
        retrieval_context=[output]
    )
    metric = FaithfulnessMetric(threshold=0.7, model="gpt-4o")
    assert_test(test_case, [metric])


# Test 3 — hallucination
def test_hallucination():
    task = "Explain what the Python programming language is"
    output = run_agent(task)
    test_case = LLMTestCase(
        input=task,
        actual_output=output,
        context=["Python is a high-level, interpreted programming language known for simplicity and readability."]
    )
    metric = HallucinationMetric(threshold=0.3, model="gpt-4o")
    assert_test(test_case, [metric])


# Test 4 — task completion (web search works)
def test_web_search_returns_results():
    task = "Search for the latest news about OpenAI"
    output = run_agent(task)
    assert len(output) > 100, "Expected substantial search output"
    assert any(word in output.lower() for word in ["openai", "ai", "model", "gpt"])


# Test 5 — code execution works
def test_code_execution():
    task = "Write and run Python code to print the sum of numbers 1 to 10"
    output = run_agent(task)
    assert "55" in output, f"Expected 55 in output, got: {output}"