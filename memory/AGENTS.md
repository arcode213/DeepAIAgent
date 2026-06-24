# Agents.md — Deep Agents Context

> This file is loaded into the deep agent's context whenever it is invoked. It
> describes the architecture, building blocks, and operating principles the agent
> should follow. Keep it concise and accurate — every line costs context tokens.

## What is a Deep Agent?

A "deep agent" is an LLM agent designed to tackle **long-horizon, multi-step
tasks** rather than single-shot tool calls. Where a shallow agent loops
"prompt → tool → respond," a deep agent adds structure so it can plan, delegate,
persist state, and stay coherent across many steps.

The pattern is built on four pillars:

1. **A detailed system prompt** — rich instructions, examples, and operating
   rules (this file is part of that).
2. **Planning** — an explicit planning tool (e.g. a TODO/scratchpad) the agent
   uses to break work into steps and track progress.
3. **Sub-agents** — the ability to spawn specialized child agents for focused
   subtasks, keeping the main agent's context clean.
4. **A virtual file system** — a shared store the agent reads from and writes to
   so state survives across steps and can be passed between sub-agents.

## Core Architecture

```
            ┌──────────────────────────────────────────┐
            │              Orchestrator Agent           │
            │  (system prompt + planning + reasoning)   │
            └───────────────┬───────────────────────────┘
                            │
        ┌───────────────────┼────────────────────────┐
        │                   │                         │
   ┌────▼─────┐       ┌─────▼──────┐           ┌──────▼──────┐
   │ Planning │       │ Sub-agents │           │ File System │
   │  (TODOs) │       │ (delegated)│           │  (state)    │
   └──────────┘       └────────────┘           └─────────────┘
        │                   │                         │
        └───────────────────┴─────────────────────────┘
                            │
                      ┌─────▼──────┐
                      │   Tools    │
                      │ (external) │
                      └────────────┘
```

### 1. Orchestrator (Main Agent)
- Owns the overall goal and the conversation with the user.
- Decides *when* to plan, *when* to delegate, and *when* to call a tool directly.
- Should keep its own context focused: offload detail to the file system and
  delegate heavy exploration to sub-agents.

### 2. Planning Tool
- A lightweight `write_todos` / scratchpad mechanism.
- The agent records the plan, marks steps in-progress/done, and re-plans as it
  learns. This combats drift on long tasks and makes progress observable.
- Update the plan *before* acting, not after.

### 3. Sub-Agents
- Spawned for well-scoped subtasks (research a topic, audit a file, draft a
  section).
- Run with their **own context window** — this prevents the main agent's context
  from being polluted by intermediate noise (a form of context engineering).
- Return only the *conclusion* to the orchestrator, not the raw work.
- Use for: breadth (parallel exploration) and isolation (keep the main thread
  clean).

### 4. Virtual File System
- A key/value or path-based store for intermediate artifacts: notes, drafts,
  fetched data, plans.
- Enables persistence across steps and hand-off between agents.
- Treat it as the agent's working memory — write findings down instead of trying
  to hold everything in the prompt.

## Context Engineering Principles

- **Offload**: move large or reference material out of the prompt into the file
  system; load it back only when needed.
- **Isolate**: give sub-agents narrow context so each does one thing well.
- **Reduce**: summarize and compact long histories; keep the working set small.
- **Retrieve**: pull the right context in at the right moment rather than
  carrying everything always.

## Operating Principles (for this agent)

- Plan before executing multi-step work; keep the TODO list current.
- Prefer delegating large or exploratory subtasks to sub-agents.
- Persist anything you'll need later to the file system — don't rely on memory.
- Return concise, high-signal results; cite where artifacts live.
- When uncertain about scope, clarify before doing irreversible work.

## Glossary

- **Long-horizon task** — work requiring many dependent steps over time.
- **Sub-agent** — a child agent invoked for a focused subtask with its own context.
- **Virtual file system** — the agent's shared, persistent working store.
- **Context engineering** — deliberately managing what goes into the model's
  context to keep it relevant, small, and effective.
