# 🤖 DeepAgent Chat

A conversational Streamlit chatbot built on the [`deepagents`](https://pypi.org/project/deepagents/)
library. It bundles **every feature** demonstrated across the notebooks in the
`deepagentsdemo/` folder into a single interactive chat app.

## Features (one per notebook)

| deepagentsdemo notebook | Feature in this app |
|---|---|
| `1-basicdeepagent.ipynb` | `create_deep_agent` with a Tavily `web_search` tool |
| `2-traveldatadeepagent.ipynb` | `save_to_excel` structured-extraction tool + downloadable `.xlsx`, step-by-step streaming |
| `03_backend.ipynb` | Switchable **State / Filesystem / Store** backends (the virtual filesystem) |
| `04_ContextEngineering.ipynb` | Editable **system prompt**, **AGENTS.md** long-term memory, and a **checkpointer** for conversation memory across turns |
| `05_Skills.ipynb` | **Skills** (`python`, `langgraph`, `aws`, `report-writing`) auto-loaded from `skills/` |
| `06_Subagents.ipynb` | A **research subagent**, optionally with **structured (Pydantic) output** |

Plus a **Plan / Todos** tab showing the agent's `write_todos` plan and a
**Files** tab showing the virtual filesystem it writes to.

## Setup

1. **API keys** — the app reads keys from the parent project's `.env`
   (`../.env`) or a local `.env`. You need at least:
   - `GROQ_API_KEY` (default model) and/or `GOOGLE_API_KEY` / `OPENAI_API_KEY`
   - `TAVILY_API_KEY` for web search

2. **Install deps** (from this folder):

   ```bash
   # with uv (recommended — matches the repo)
   uv run streamlit run app.py

   # or with pip
   pip install -r requirements.txt
   streamlit run app.py
   ```

The app opens at <http://localhost:8501>.

## How to use

- Use the **sidebar** to pick a model, choose a backend, and toggle
  capabilities (web search, Excel, skills, subagents, memory). Click
  **Apply / Rebuild** after changing settings.
- Type in the chat box. The status panel streams the agent's tool calls and
  subagent activity step by step.
- Check the **Files** and **Plan / Todos** tabs to see the agent's working
  state.

### Things to try

- *"What skills do you have available, and when would you use each?"* — exercises **skills**.
- *"Research recent advances in quantum computing."* — exercises the **research subagent**.
- *"Find 10 travel agencies in Pakistan with name, city, email, contact and save them to Excel."* — exercises **web search + save_to_excel**.
- *"Create a file at /notes/todo.txt with my three tasks, then read it back."* — exercises the **backend / virtual filesystem**.
- *"Who are you and what should you follow?"* — exercises **AGENTS.md memory**.

## Layout

```
DeepAgentProject/
├── app.py              # Streamlit UI + chat loop
├── agent_factory.py    # wires every deepagents feature into one agent
├── tools.py            # web_search + save_to_excel tools
├── skills/             # skill.md packs (python, langgraph, aws, report-writing)
├── memory/AGENTS.md    # long-term memory loaded into the agent
├── outputs/            # generated .xlsx files (created at runtime)
└── workspace/          # Filesystem-backend virtual disk (created at runtime)
```
