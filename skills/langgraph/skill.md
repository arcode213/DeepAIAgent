# Skill: LangGraph

> Loaded into the deep agent's context when a task involves designing or building
> agentic workflows with LangGraph / LangChain. Read this first, then
> `instruction.md` for the build procedure and `example.md` for runnable code.

## Purpose

This skill makes the agent effective at building **stateful, controllable,
multi-step agent graphs** with LangGraph. LangGraph models an LLM application as
a directed graph of nodes operating over shared state, which gives you explicit
control over branching, loops, persistence, streaming, and human-in-the-loop —
things that are hard to express as a linear chain.

## When to use this skill

- Building an agent, chatbot, or workflow that has **state, branching, cycles,
  or multiple cooperating nodes**.
- Tool-calling agents (ReAct-style: model → tools → model loops).
- Routing between steps based on content or classification.
- Retry/reflection/self-correction loops.
- Multi-agent systems (supervisor/worker, hierarchical teams).
- Adding **persistence** (memory, resume), **streaming**, or **human approval
  gates** to an LLM workflow.

If the task is a single LLM call or a simple linear prompt→model→output chain,
plain LangChain (LCEL) or a direct SDK call may be simpler — note that.

## Core mental model

LangGraph represents a workflow as a **graph** with these primitives:

- **State** — a typed, shared object (usually a `TypedDict`, optionally a
  Pydantic model) that flows through the graph. Nodes receive the current state
  and return **partial updates** that get merged in.
- **Nodes** — functions (or runnables) `state -> partial_state`. Each node does
  one unit of work: call the model, run a tool, transform data, decide a route.
- **Edges** — connections between nodes that define control flow.
  - **Normal edges** (`add_edge`) always go A → B.
  - **Conditional edges** (`add_conditional_edges`) call a router function over
    the state and pick the next node — this is how you branch and loop.
- **Reducers** — define how each state key is merged when a node returns it. The
  default overwrites; `add_messages` (and `operator.add`) append. Reducers are
  what make accumulation and concurrency safe.
- **Checkpointers** — persist state per **thread** so a graph can pause, resume,
  recover, support memory across turns, and enable human-in-the-loop.
- **`START` / `END`** — sentinel nodes for the graph's entry and exit.

## Key building blocks (API surface)

```python
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import create_react_agent, ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command, interrupt
```

- `StateGraph(StateSchema)` — the builder.
- `.add_node(name, fn)` / `.add_edge(a, b)` / `.add_conditional_edges(src, router, mapping)`.
- `.compile(checkpointer=..., interrupt_before=[...])` → a runnable app.
- `.invoke(input, config)`, `.stream(...)`, `.astream(...)`, `.astream_events(...)`.
- Prebuilt: `create_react_agent(model, tools)` for a ready ReAct agent;
  `ToolNode(tools)` to execute tool calls; `tools_condition` to route
  "tools vs end".
- `Command(update={...}, goto="next")` — update state **and** route from inside
  a node in one return.
- `interrupt(value)` / `interrupt_before=[node]` — pause for human input.

## Common architectural patterns

1. **ReAct agent** — `model → (tools? loop back : END)` via `tools_condition`.
2. **Router / classifier** — a node classifies input, conditional edges fan out
   to specialized branches.
3. **Reflection / self-correction** — generate → critique → (revise loop until
   good or max iterations).
4. **Plan-and-execute** — a planner node produces steps; an executor loops over
   them; a replanner adjusts.
5. **Supervisor multi-agent** — a supervisor node routes to worker agents
   (each itself a subgraph) and aggregates.
6. **Human-in-the-loop** — `interrupt_before` an action node; resume with the
   human's decision after review.
7. **Map-reduce / fan-out** — `Send` API to spawn parallel node executions over
   a list, then reduce results.

## Core principles

1. **State is the contract.** Define it explicitly, keep it minimal and typed.
   Everything a node needs must be in state (or config), and everything it
   produces must be returned as a partial update.
2. **One responsibility per node.** Small nodes are testable and composable.
3. **Branch with conditional edges; keep routing logic in one place.**
4. **Use reducers for anything that accumulates** (messages, collected items) so
   updates append instead of clobbering — essential with parallel nodes.
5. **Persist with a checkpointer.** Required for memory, resume, and HITL; always
   pass a `thread_id` in config when one is set.
6. **Bound your loops.** Every cycle needs a termination condition and a
   max-iteration guard; set/raise `recursion_limit` deliberately.
7. **Stream for UX.** Use `.stream()` / `.astream_events()` to surface progress
   on long runs.
8. **Keep state lean.** It travels through every node and gets checkpointed —
   don't stuff large blobs in it; reference them (file paths, IDs) instead.

## Version awareness

LangGraph and LangChain evolve quickly and APIs shift across minor versions
(prebuilt helpers, message types, checkpointer packages like
`langgraph-checkpoint-sqlite`). **Check the installed versions** (`pip show
langgraph langchain`) before relying on a specific helper, and prefer the
patterns the project already uses.

## Companion files

- `instruction.md` — the step-by-step procedure for designing, building,
  running, and debugging a LangGraph workflow.
- `example.md` — multiple runnable graphs: ReAct agent, custom routing,
  reflection loop, and human-in-the-loop.
