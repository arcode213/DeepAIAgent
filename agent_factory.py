"""Builds a Deep Agent that combines every feature shown in deepagentsdemo.

Features wired in here (one per notebook):
  * create_deep_agent + custom tools          -> 1-basicdeepagent.ipynb
  * structured Excel extraction tool           -> 2-traveldatadeepagent.ipynb
  * pluggable backends (State/Filesystem/Store)-> 03_backend.ipynb
  * context engineering: system prompt, AGENTS.md memory, checkpointer
                                               -> 04_ContextEngineering.ipynb
  * skills loaded from /skills/*               -> 05_Skills.ipynb
  * subagents (incl. structured response)      -> 06_Subagents.ipynb
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Literal

from pydantic import BaseModel, Field

from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend, StateBackend, StoreBackend
from deepagents.backends.utils import create_file_data
from langgraph.checkpoint.memory import MemorySaver
from langgraph.store.memory import InMemoryStore

from tools import save_to_excel, web_search

HERE = Path(__file__).parent
SKILLS_DIR = HERE / "skills"
MEMORY_DIR = HERE / "memory"

# ---- Models available (from across the notebooks) ----------------------------
MODELS = {
    "Groq · llama-3.3-70b-versatile": ("groq", "groq:llama-3.3-70b-versatile"),
    "Google · gemini-2.5-flash": ("google", "gemini-2.5-flash"),
    "Google · gemini-3.5-flash": ("google", "gemini-3.5-flash"),
    "OpenAI · gpt-4o-mini": ("openai", "openai:gpt-4o-mini"),
}

BACKENDS = ["State", "Filesystem", "Store"]

DEFAULT_SYSTEM_PROMPT = (
    "You are a helpful Deep Agent assistant. You can plan with a todo list, "
    "delegate to subagents, read your skills, search the web, persist files to "
    "a virtual filesystem, and remember context across the conversation. "
    "Be thorough on multi-step tasks: plan first, use the right tool or skill, "
    "and write intermediate findings to files instead of holding everything in "
    "your context.\n\n"
    "FORMAT EVERY FINAL ANSWER AS CLEAN, WELL-STRUCTURED MARKDOWN, the way "
    "ChatGPT or Claude would:\n"
    "- Open with a one or two sentence summary of the answer.\n"
    "- Use `##` / `###` headings to break the answer into clear sections.\n"
    "- Use bullet or numbered lists for steps, options, and groups of facts.\n"
    "- Use a Markdown table when presenting structured/tabular data.\n"
    "- Use **bold** for key terms and `inline code` for file paths, commands, "
    "and identifiers; use fenced code blocks for code.\n"
    "- When you cite web sources, add a `### Sources` section with links.\n"
    "Keep it scannable and well-spaced — never return one dense wall of text."
)


# ---- Structured output for the research subagent (notebook 6) -----------------
class ResearchFinding(BaseModel):
    """Structured findings from a research task."""

    summary: str = Field(description="Summary of findings")
    confidence: float = Field(description="Confidence score from 0 to 1")
    sources: List[str] = Field(description="List of source URLs")


@dataclass
class AgentConfig:
    """Everything the sidebar can toggle."""

    model_label: str = next(iter(MODELS))
    backend: Literal["State", "Filesystem", "Store"] = "State"
    system_prompt: str = DEFAULT_SYSTEM_PROMPT
    enable_web_search: bool = True
    enable_excel: bool = True
    enable_skills: bool = True
    enable_subagents: bool = True
    enable_memory: bool = True  # load AGENTS.md as long-term memory
    structured_research: bool = False


def _build_model(label: str):
    provider, model_id = MODELS[label]
    if provider == "google":
        # Gemini is a thinking model; thinking_budget=0 keeps tool-calling
        # reliable inside the big deep-agent prompt (see notebook 2).
        from langchain_google_genai import ChatGoogleGenerativeAI

        return ChatGoogleGenerativeAI(
            model=model_id, thinking_budget=0, max_tokens=8192, temperature=0
        )
    # groq:/openai: strings are resolved by deepagents/init_chat_model.
    return model_id


def _list_skill_paths() -> list[str]:
    """Virtual paths for each skill.md, e.g. '/skills/python/skill.md'."""
    return [
        f"/skills/{p.parent.name}/skill.md"
        for p in sorted(SKILLS_DIR.glob("*/skill.md"))
    ]


def skill_files() -> dict:
    """File payload that seeds the agent's virtual FS with skill content."""
    files = {}
    for p in sorted(SKILLS_DIR.glob("*/skill.md")):
        vpath = f"/skills/{p.parent.name}/skill.md"
        files[vpath] = create_file_data(p.read_text(encoding="utf-8"))
    return files


def agents_md_text() -> str:
    md = MEMORY_DIR / "AGENTS.md"
    return md.read_text(encoding="utf-8") if md.exists() else ""


def build_agent(cfg: AgentConfig):
    """Create the deep agent + the initial `files` payload to seed it with.

    Memory/skill wiring is backend-aware:
      * State      -> seeded into agent state via the `files` input (returned).
      * Filesystem -> read straight from disk (root_dir = project folder).
      * Store      -> written into the store namespace the backend reads from.

    Returns (agent, store, seed_files).
    """
    model = _build_model(cfg.model_label)
    store = InMemoryStore()
    has_memory = cfg.enable_memory and bool(agents_md_text())

    # Tools -------------------------------------------------------------------
    tools = []
    if cfg.enable_web_search:
        tools.append(web_search)
    if cfg.enable_excel:
        tools.append(save_to_excel)

    # Subagents (notebook 6) --------------------------------------------------
    subagents = None
    if cfg.enable_subagents:
        research_subagent = {
            "name": "research-agent",
            "description": "Delegate in-depth, multi-source research questions here.",
            "system_prompt": (
                "You are a meticulous researcher. Search several times, "
                "cross-check sources, and return a concise, cited synthesis."
            ),
            "tools": [web_search],
            "model": "groq:llama-3.3-70b-versatile",
        }
        if cfg.structured_research:
            research_subagent["response_format"] = ResearchFinding
        subagents = [research_subagent]

    # Skills + memory (notebooks 3, 4 & 5) -----------------------------------
    skills = ["/skills/"] if cfg.enable_skills else None
    memory = ["/memory/AGENTS.md"] if has_memory else None
    seed_files: dict = {}

    if cfg.backend == "Filesystem":
        # Real skills/ and memory/ folders on disk are visible to the agent.
        backend = FilesystemBackend(root_dir=str(HERE), virtual_mode=True)
    elif cfg.backend == "Store":
        # The backend reads files from this namespace; seed it directly.
        backend = StoreBackend(store=store, namespace=lambda rt: ("files",))
        if cfg.enable_skills:
            for vpath, data in skill_files().items():
                store.put(("files",), vpath, data)
        if has_memory:
            store.put(("files",), "/memory/AGENTS.md",
                      create_file_data(agents_md_text()))
    else:  # State (default) — seed via the `files` input on the first turn.
        backend = StateBackend()
        if cfg.enable_skills:
            seed_files.update(skill_files())
        if has_memory:
            seed_files["/memory/AGENTS.md"] = create_file_data(agents_md_text())

    agent = create_deep_agent(
        model=model,
        tools=tools or None,
        system_prompt=cfg.system_prompt,
        backend=backend,
        subagents=subagents,
        skills=skills,
        memory=memory,
        store=store,
        checkpointer=MemorySaver(),  # conversation memory across turns
    )
    return agent, store, seed_files
