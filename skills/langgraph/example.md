# Examples: LangGraph Skill

Runnable, idiomatic graphs covering the most common patterns: a ReAct agent,
custom routing, a reflection loop, and human-in-the-loop. Adapt the model class
to whatever the project uses.

---

## Example 1 — ReAct-style agent with one tool

```python
from typing import Annotated, TypedDict

from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver


# 1. State: messages accumulate via the add_messages reducer.
class State(TypedDict):
    messages: Annotated[list, add_messages]


# 2. A tool the agent can call.
@tool
def multiply(a: int, b: int) -> int:
    """Multiply two integers."""
    return a * b


tools = [multiply]
llm = ChatOpenAI(model="gpt-4o-mini").bind_tools(tools)


# 3. The model node returns a partial state update.
def call_model(state: State) -> dict:
    return {"messages": [llm.invoke(state["messages"])]}


# 4. Wire the graph: model -> (tools? -> model) -> END
builder = StateGraph(State)
builder.add_node("model", call_model)
builder.add_node("tools", ToolNode(tools))

builder.add_edge(START, "model")
builder.add_conditional_edges("model", tools_condition)  # -> "tools" or END
builder.add_edge("tools", "model")

app = builder.compile(checkpointer=MemorySaver())

# 5. Run with a thread_id so state persists per conversation.
config = {"configurable": {"thread_id": "demo-1"}}
result = app.invoke({"messages": [("user", "What is 12 times 8?")]}, config=config)
print(result["messages"][-1].content)
```

The same thing in one line with the prebuilt helper:

```python
from langgraph.prebuilt import create_react_agent
agent = create_react_agent(llm, tools, checkpointer=MemorySaver())
```

---

## Example 2 — Classifier with custom conditional routing

```python
from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages


class State(TypedDict):
    messages: Annotated[list, add_messages]
    intent: str


def classify(state: State) -> dict:
    text = state["messages"][-1].content.lower()
    intent = "refund" if "refund" in text else "general"
    return {"intent": intent}


def route(state: State) -> str:
    return "refund_flow" if state["intent"] == "refund" else "general_flow"


def refund_flow(state: State) -> dict:
    return {"messages": [("assistant", "Starting your refund...")]}


def general_flow(state: State) -> dict:
    return {"messages": [("assistant", "How can I help?")]}


builder = StateGraph(State)
builder.add_node("classify", classify)
builder.add_node("refund_flow", refund_flow)
builder.add_node("general_flow", general_flow)

builder.add_edge(START, "classify")
builder.add_conditional_edges(
    "classify", route,
    {"refund_flow": "refund_flow", "general_flow": "general_flow"},
)
builder.add_edge("refund_flow", END)
builder.add_edge("general_flow", END)

app = builder.compile()
```

---

## Example 3 — Reflection / self-correction loop (bounded)

```python
from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages


class State(TypedDict):
    messages: Annotated[list, add_messages]
    draft: str
    critique: str
    revisions: int          # bound the loop


MAX_REVISIONS = 3


def generate(state: State) -> dict:
    # produce/revise a draft using state["critique"] if present
    return {"draft": "...", "revisions": state.get("revisions", 0) + 1}


def critique(state: State) -> dict:
    # evaluate the draft; empty critique == good enough
    return {"critique": "" if state["draft"] else "needs work"}


def should_continue(state: State) -> str:
    if not state["critique"] or state["revisions"] >= MAX_REVISIONS:
        return END
    return "generate"


builder = StateGraph(State)
builder.add_node("generate", generate)
builder.add_node("critique", critique)
builder.add_edge(START, "generate")
builder.add_edge("generate", "critique")
builder.add_conditional_edges("critique", should_continue, {"generate": "generate", END: END})

app = builder.compile()
```

The `revisions` counter plus the `MAX_REVISIONS` check guarantees termination.

---

## Example 4 — Human-in-the-loop with interrupt

```python
from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver


class State(TypedDict):
    messages: Annotated[list, add_messages]
    approved: bool


def propose_action(state: State) -> dict:
    return {"messages": [("assistant", "I plan to delete 3 records. Approve?")]}


def execute_action(state: State) -> dict:
    return {"messages": [("assistant", "Done.")]}


builder = StateGraph(State)
builder.add_node("propose_action", propose_action)
builder.add_node("execute_action", execute_action)
builder.add_edge(START, "propose_action")
builder.add_edge("propose_action", "execute_action")
builder.add_edge("execute_action", END)

# Pause BEFORE executing so a human can review.
app = builder.compile(checkpointer=MemorySaver(), interrupt_before=["execute_action"])

config = {"configurable": {"thread_id": "hitl-1"}}
app.invoke({"messages": [("user", "clean up old records")]}, config=config)
# ... graph pauses. Inspect state, get human approval, then resume:
app.invoke(None, config=config)   # continues from the checkpoint
```

---

## Example 5 — Observing the path with streaming

```python
for step in app.stream(
    {"messages": [("user", "What is 12 times 8?")]},
    config={"configurable": {"thread_id": "demo-1"}},
    stream_mode="updates",          # per-node partial updates
):
    print(step)                     # e.g. {'model': {...}} then {'tools': {...}}
```

---

## What these demonstrate

- State as a `TypedDict` with `add_messages` reducer; nodes return **partial**
  updates, never mutate state.
- `tools_condition` for the standard agent loop; custom router functions mapped
  to node keys for branching.
- Bounded loops (counter + max) to guarantee termination.
- A checkpointer + `thread_id` for persistence and resume.
- `interrupt_before` for human approval gates.
- `stream(..., stream_mode="updates")` to watch the executed path.
