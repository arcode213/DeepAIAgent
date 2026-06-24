# Instructions: LangGraph Skill

The procedure the deep agent follows to design, build, run, and debug a
LangGraph workflow. Work through the phases in order.

---

## Phase 1 — Clarify the workflow

- Describe the workflow as a graph of steps in one or two sentences.
- Identify the three things that define a LangGraph app:
  1. **State** — what data flows through it.
  2. **Control flow** — where it branches, loops, and ends.
  3. **Side effects** — which tools/models/external calls it makes.
- Decide whether it needs: persistence (memory/resume), tools, human approval,
  streaming, or multiple agents.
- Match the design to a known pattern (ReAct, router, reflection, plan-execute,
  supervisor, HITL, map-reduce) where one fits.
- Check installed `langgraph` / `langchain` versions and existing project
  conventions before choosing APIs.

## Phase 2 — Define the state

- Create a `TypedDict` (or Pydantic model) with **only** the fields the graph
  needs end-to-end.
- Choose reducers per key:
  - Conversation history → `Annotated[list, add_messages]` (appends, dedupes by
    id, handles message objects).
  - Accumulating lists → `Annotated[list, operator.add]`.
  - Single-value fields → default (last write wins).
- Keep large artifacts **out** of state — store a reference (path, id) instead.

```python
from typing import Annotated, TypedDict
from langgraph.graph.message import add_messages

class State(TypedDict):
    messages: Annotated[list, add_messages]
    # add only what the graph truly needs to thread through
```

## Phase 3 — Implement nodes

- Each node is a function `def node(state) -> dict:` returning a **partial**
  update (only the keys it changes). Never mutate `state` in place — return new
  values.
- One responsibility per node. Push tool execution into `ToolNode`; keep model
  calls in their own node.
- Read config (model handles, thread settings) via the `config` argument or
  closures; don't hard-code secrets.
- For "update state and decide where to go next" in one step, return a
  `Command(update={...}, goto="next_node")`.

## Phase 4 — Wire the graph

- `builder = StateGraph(State)`; register nodes with `add_node`.
- Set the entry: `builder.add_edge(START, "first_node")`.
- Add normal edges for unconditional transitions.
- Add **conditional edges** for branching/looping:

  ```python
  def route(state) -> str:
      ...  # inspect state, return a key
  builder.add_conditional_edges("node", route, {"a": "node_a", "b": END})
  ```

- For the standard agent loop, use the prebuilt `tools_condition`:
  `model → tools_condition → (ToolNode → back to model | END)`.
- Ensure **every path can reach `END`**.

## Phase 5 — Compile

- `app = builder.compile(checkpointer=...)`.
  - Dev / in-memory: `MemorySaver()`.
  - Persistent: a SQLite/Postgres checkpointer (separate package).
- For human-in-the-loop, pass `interrupt_before=["action_node"]` (or call
  `interrupt(...)` inside a node).
- Consider `app.get_graph().draw_mermaid()` to visualize and sanity-check the
  topology.

## Phase 6 — Run

- With a checkpointer, **always** pass a thread id:

  ```python
  config = {"configurable": {"thread_id": "user-123"}}
  result = app.invoke({"messages": [("user", "...")]}, config=config)
  ```

- Use streaming to observe steps:
  - `for chunk in app.stream(input, config, stream_mode="updates"):` → per-node
    state deltas.
  - `stream_mode="values"` → full state after each step.
  - `app.astream_events(..., version="v2")` → token/tool-level events for UIs.
- Resume after an interrupt by invoking again with the same `thread_id` (and a
  `Command(resume=...)` where applicable).

## Phase 7 — Verify

- Run the graph on a representative input and confirm the **path taken** matches
  the design (use `stream_mode="updates"` to watch node-by-node).
- Test routing logic in isolation (call the router function with crafted states).
- Test at least one tool call end-to-end.
- Verify termination: confirm loops stop and `END` is reached; check the
  `recursion_limit` is high enough for real inputs but still bounds runaways.

## Phase 8 — Report

- Describe the node/edge topology (a short list or a Mermaid diagram).
- State where state is persisted (checkpointer + thread model) and how to run it.
- Note tools used, any HITL pauses, and limitations.

---

## Debugging guide

| Symptom | Likely cause | Fix |
|---|---|---|
| `GraphRecursionError` | Unbounded loop / missing exit edge | Add a termination condition; raise `recursion_limit`; ensure router can return `END`. |
| State key keeps overwriting | Missing reducer | Annotate the key with `add_messages` / `operator.add`. |
| Memory not persisting | No checkpointer or no `thread_id` | Compile with a checkpointer and pass `configurable.thread_id`. |
| Parallel nodes clobber state | Concurrent writes to a non-reduced key | Add a reducer so writes merge. |
| Tool never called | Model not bound to tools / wrong routing | `llm.bind_tools(tools)`; use `tools_condition`. |
| Interrupt doesn't pause | Wrong node name in `interrupt_before` | Match the exact node key; or use `interrupt()` inside the node. |

## Guardrails

- Don't put unbounded or large data in state — it travels through every node and
  is checkpointed on every step.
- Every cycle needs a termination condition **and** a max-iteration guard.
- Always set a terminal path to `END`.
- Keep API keys in environment variables, never hard-coded.
- Pin/respect the installed LangGraph & LangChain versions; verify a helper
  exists in that version before using it.
- Make nodes deterministic where possible and isolate side effects so the graph
  is testable and resumable.
