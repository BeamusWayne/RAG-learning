from typing_extensions import TypedDict, Literal
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
import os
from pathlib import Path
from langgraph.graph import StateGraph, START, END

IMG_DIR = Path(__file__).resolve().parent / "img"
llm = ChatOpenAI(
# Graph state
    model="qwen-max",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
)


class State(TypedDict):
    joke: str
    topic: str
    feedback: str
    funny_or_not: str


# Schema for structured output to use in evaluation
class Feedback(BaseModel):
    grade: Literal["funny", "not funny"] = Field(
        description="Decide if the joke is funny or not.",
    )
    feedback: str = Field(
        description="If the joke is not funny, provide feedback on how to improve it.",
    )


# Augment the LLM with schema for structured output
evaluator = llm.with_structured_output(Feedback)


# Nodes
def llm_call_generator(state: State):
    """LLM generates a joke"""

    if state.get("feedback"):
        msg = llm.invoke(
            f"Write a joke about {state['topic']} but take into account the feedback: {state['feedback']}"
        )
    else:
        msg = llm.invoke(f"Write a joke about {state['topic']}")
    return {"joke": msg.content}


def llm_call_evaluator(state: State):
    """LLM evaluates the joke"""

    prompt = (
        "Grade the joke below. Reply in JSON format with 'grade' (one of 'funny' or 'not funny') "
        "and 'feedback' (how to improve if not funny). Joke: " + state["joke"]
    )
    grade = evaluator.invoke(prompt)
    return {"funny_or_not": grade.grade, "feedback": grade.feedback}


# Conditional edge function to route back to joke generator or end based upon feedback from the evaluator
def route_joke(state: State):
    """Route back to joke generator or end based upon feedback from the evaluator"""

    if state["funny_or_not"] == "funny":
        return "Accepted"
    elif state["funny_or_not"] == "not funny":
        return "Rejected + Feedback"


# Build workflow
optimizer_builder = StateGraph(State)

# Add the nodes
optimizer_builder.add_node("llm_call_generator", llm_call_generator)
optimizer_builder.add_node("llm_call_evaluator", llm_call_evaluator)

# Add edges to connect nodes
optimizer_builder.add_edge(START, "llm_call_generator")
optimizer_builder.add_edge("llm_call_generator", "llm_call_evaluator")
optimizer_builder.add_conditional_edges(
    "llm_call_evaluator",
    route_joke,
    {  # Name returned by route_joke : Name of next node to visit
        "Accepted": END,
        "Rejected + Feedback": "llm_call_generator",
    },
)

# Compile the workflow
optimizer_workflow = optimizer_builder.compile()

# Show the workflow
IMG_DIR.mkdir(parents=True, exist_ok=True)
graph_path = IMG_DIR / "05_evaluator_optimizer_graph.png"
with open(graph_path, "wb") as f:
    f.write(optimizer_workflow.get_graph().draw_mermaid_png())
print(f"Graph saved to {graph_path}")

# Invoke
state = optimizer_workflow.invoke({"topic": "Cats"})
print(state["joke"])