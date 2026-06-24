"""DeepAgent Chat — a conversational Streamlit chatbot built on `deepagents`.

It folds together every feature demonstrated in the deepagentsdemo notebooks:
planning todos, a virtual filesystem (State/Filesystem/Store backends), skills,
subagents, web search, Excel extraction, AGENTS.md long-term memory, and
checkpointed conversation memory — all driven from the sidebar.

Run:  streamlit run app.py
"""
from __future__ import annotations

import os
import re
import uuid

import streamlit as st
from dotenv import load_dotenv

# Load API keys from the parent project's .env (OPENAI/GROQ/GOOGLE/TAVILY).
# override=True so that EDITING .env and restarting picks up the new keys —
# without it, a stale key already in os.environ would silently win and you'd
# keep hitting the old key's quota/limit even after pasting a fresh one.
load_dotenv(override=True)
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"), override=True)

from agent_factory import (  # noqa: E402  (after load_dotenv)
    BACKENDS,
    MODELS,
    AgentConfig,
    build_agent,
)
from ui import BOT_AVATAR, USER_AVATAR, hero, inject_css, welcome  # noqa: E402

st.set_page_config(page_title="DeepAgent Chat", page_icon="🤖", layout="wide")
inject_css()

# Example prompts shown as clickable chips on the welcome screen.
SUGGESTIONS = [
    ("🧠 Explore skills", "What skills do you have available, and when would you use each?"),
    ("🔬 Research a topic", "Research recent advances in quantum computing and summarize with sources."),
    ("📊 Extract to Excel", "Find 8 popular travel agencies in Dubai with name, city, email and contact, then save them to Excel."),
    ("📝 Use the filesystem", "Create a file at /notes/plan.txt with a 3-step launch plan, then read it back to me."),
]


# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------
def _new_thread() -> str:
    return str(uuid.uuid4())


_defaults = {
    "messages": [],
    "thread_id": _new_thread(),
    "agent": None,
    "seed_files": {},
    "seeded": False,
    "last_files": {},
    "last_todos": [],
    "pending": None,  # a queued prompt from a suggestion chip
}
for k, v in _defaults.items():
    st.session_state.setdefault(k, v)


# ---------------------------------------------------------------------------
# Sidebar — configure every deep-agent feature
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown('<div class="side-title">🤖 DeepAgent Chat</div>', unsafe_allow_html=True)
    st.markdown('<div class="side-sub">Configure the agent, then chat.</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-label">Model & Backend</div>', unsafe_allow_html=True)
    model_label = st.selectbox("Model", list(MODELS.keys()), index=0, label_visibility="collapsed")
    backend = st.radio(
        "Backend", BACKENDS, index=0, horizontal=True,
        help="State = in-memory · Filesystem = local disk · Store = cross-thread store",
    )

    st.markdown('<div class="section-label">Capabilities</div>', unsafe_allow_html=True)
    enable_web_search = st.toggle("🔍 Web search (Tavily)", value=True)
    enable_excel = st.toggle("📊 Save to Excel", value=True)
    enable_skills = st.toggle("🧠 Skills (python · langgraph · aws · report)", value=True)
    enable_subagents = st.toggle("👥 Subagents (research-agent)", value=True)
    structured_research = st.toggle(
        "↳ Structured research output", value=False, disabled=not enable_subagents
    )
    enable_memory = st.toggle("📌 Long-term memory (AGENTS.md)", value=True)

    with st.expander("⚙️ System prompt"):
        system_prompt = st.text_area(
            "System prompt", value=AgentConfig().system_prompt, height=170,
            label_visibility="collapsed",
        )

    col_a, col_b = st.columns(2)
    apply_clicked = col_a.button("✨ Apply", use_container_width=True, type="primary")
    reset_clicked = col_b.button("🗑️ Reset", use_container_width=True)

    st.markdown('<div class="section-label">API keys</div>', unsafe_allow_html=True)
    for k in ["GROQ_API_KEY", "GOOGLE_API_KEY", "OPENAI_API_KEY", "TAVILY_API_KEY"]:
        dot = "🟢" if os.getenv(k) else "🔴"
        st.markdown(f'<div class="keyrow">{dot} {k}</div>', unsafe_allow_html=True)


def current_config() -> AgentConfig:
    return AgentConfig(
        model_label=model_label,
        backend=backend,
        system_prompt=system_prompt,
        enable_web_search=enable_web_search,
        enable_excel=enable_excel,
        enable_skills=enable_skills,
        enable_subagents=enable_subagents,
        enable_memory=enable_memory,
        structured_research=structured_research,
    )


def ensure_agent(force: bool = False):
    if st.session_state.agent is None or force:
        with st.spinner("Building deep agent…"):
            agent, _store, seed_files = build_agent(current_config())
            st.session_state.agent = agent
            st.session_state.seed_files = seed_files
            st.session_state.seeded = False
            st.session_state.thread_id = _new_thread()


if reset_clicked:
    st.session_state.messages = []
    st.session_state.thread_id = _new_thread()
    st.session_state.seeded = False
    st.session_state.last_files = {}
    st.session_state.last_todos = []
    st.session_state.pending = None
    st.rerun()

if apply_clicked:
    ensure_agent(force=True)
    st.session_state.messages = []
    st.toast("Agent rebuilt with new settings.", icon="✨")


# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
active_pills = ["Planning todos", f"{backend} backend"]
if enable_web_search:
    active_pills.append("Web search")
if enable_excel:
    active_pills.append("Excel export")
if enable_skills:
    active_pills.append("Skills")
if enable_subagents:
    active_pills.append("Subagents")
if enable_memory:
    active_pills.append("Memory")
hero(active_pills)


# ---------------------------------------------------------------------------
# Core: run one user turn through the agent
# ---------------------------------------------------------------------------
def _friendly_error(e: Exception) -> str:
    """Turn a raw provider exception into a clear, actionable chat message."""
    msg = str(e)
    low = msg.lower()
    if any(s in low for s in ("rate limit", "ratelimit", "429", "resource_exhausted",
                              "quota", "tokens per day", "tpd")):
        return (
            "⚠️ **API rate limit / quota reached** for the selected model.\n\n"
            "Your current model has hit its provider quota (this is an account "
            "limit, not an app error). To keep chatting:\n\n"
            "- Pick a **different model** in the sidebar (e.g. switch Groq → "
            "Google or OpenAI), then click **✨ Apply**, or\n"
            "- Wait for the quota window to reset, or upgrade your provider tier.\n\n"
            f"**Technical detail**\n\n```\n{msg[:600]}\n```"
        )
    return (
        "❌ **The agent stopped before finishing.**\n\n"
        f"```\n{msg[:800]}\n```\n\n"
        "Try rephrasing, or switch models in the sidebar and click **✨ Apply**."
    )


# ---- Per-response detail collection + tabbed rendering ----------------------
_URL_RE = re.compile(r'https?://[^\s\)\]\}"\'<>]+')


def _extract_urls(text: str) -> list[str]:
    return _URL_RE.findall(text or "")


def _file_content(data) -> str:
    content = data.get("content", data) if isinstance(data, dict) else data
    if isinstance(content, list):
        content = "\n".join(map(str, content))
    return str(content)


def _collect_details(final_state, answer: str, prev_files: dict):
    """Pull this turn's process steps, sources, and changed files out of state.

    Returns (steps_markdown, sources_list, changed_files_dict).
    """
    msgs = final_state.get("messages", []) if final_state else []
    # Scope to the current turn: everything after the last user message.
    last_human = -1
    for i, m in enumerate(msgs):
        if getattr(m, "type", None) == "human":
            last_human = i
    turn = msgs[last_human + 1:] if last_human >= 0 else msgs

    step_lines: list[str] = []
    sources: list[str] = []
    seen: set[str] = set()
    n = 0
    for m in turn:
        for tc in getattr(m, "tool_calls", None) or []:
            n += 1
            name = tc.get("name", "tool")
            args = tc.get("args", {}) or {}
            preview = ", ".join(f"{k}={str(v)[:50]}" for k, v in args.items())
            step_lines.append(
                f"{n}. 🔧 **Called** `{name}`" + (f" — `{preview}`" if preview else "")
            )
        if getattr(m, "type", None) == "tool":
            name = getattr(m, "name", "tool")
            body = m.content if isinstance(m.content, str) else str(m.content)
            step_lines.append(f"&nbsp;&nbsp;&nbsp;↩️ result from `{name}` ({len(body):,} chars)")
            for u in _extract_urls(body):
                if u not in seen:
                    seen.add(u)
                    sources.append(u)

    # Also harvest links cited directly in the final answer.
    for u in _extract_urls(answer):
        if u not in seen:
            seen.add(u)
            sources.append(u)

    # Files created or changed during this turn (diff against pre-turn snapshot).
    changed: dict = {}
    for path, data in (final_state.get("files", {}) if final_state else {}).items():
        c = _file_content(data)
        if prev_files.get(path) != c:
            changed[path] = c

    return "\n".join(step_lines), sources, changed


def _render_assistant(msg: dict) -> None:
    """Render one assistant message as sub-tabs: Answer | Sources | Process | Files."""
    answer = msg.get("content") or "_(no text response)_"
    sources = msg.get("sources") or []
    steps = msg.get("steps") or ""
    files = msg.get("files") or {}

    # Simple replies (no tools/sources/files) render as a plain document — no tabs.
    if not sources and not steps and not files:
        st.markdown(answer)
        return

    labels = ["💬 Answer"]
    if sources:
        labels.append(f"🔗 Sources ({len(sources)})")
    if steps:
        labels.append("🧭 Process")
    if files:
        labels.append(f"📁 Files ({len(files)})")

    tabs = iter(st.tabs(labels))
    with next(tabs):
        st.markdown(answer)
    if sources:
        with next(tabs):
            st.markdown("\n".join(f"- [{u}]({u})" for u in sources))
    if steps:
        with next(tabs):
            st.markdown(steps, unsafe_allow_html=True)
    if files:
        with next(tabs):
            for path, content in files.items():
                st.markdown(f"**`{path}`**")
                lang = "python" if path.endswith(".py") else "markdown"
                st.code(content[:5000], language=lang)


def run_turn(prompt: str):
    ensure_agent()
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar=USER_AVATAR):
        st.markdown(prompt)

    config = {
        "configurable": {"thread_id": st.session_state.thread_id},
        "recursion_limit": 100,
    }
    inputs: dict = {"messages": [{"role": "user", "content": prompt}]}
    if not st.session_state.seeded and st.session_state.seed_files:
        inputs["files"] = st.session_state.seed_files
        st.session_state.seeded = True

    # Snapshot files before the turn so we can show only what changed.
    prev_files = {
        p: _file_content(d) for p, d in (st.session_state.last_files or {}).items()
    }

    with st.chat_message("assistant", avatar=BOT_AVATAR):
        status = st.status("Thinking…", expanded=True)
        final_state, steps, err = None, 0, None
        try:
            for state in st.session_state.agent.stream(
                inputs, stream_mode="values", config=config
            ):
                final_state = state
                steps += 1
                msgs = state.get("messages", [])
                if msgs:
                    last = msgs[-1]
                    for tc in getattr(last, "tool_calls", None) or []:
                        status.write(f"🔧 calling `{tc.get('name', 'tool')}`")
                    if getattr(last, "name", None):
                        status.write(f"↩️ result from `{last.name}`")
                status.update(label=f"Working… step {steps}")
        except Exception as e:  # noqa: BLE001
            err = e

        if err is not None:
            status.update(label="Stopped early", state="error")
        else:
            status.update(label=f"Done · {steps} steps", state="complete", expanded=False)

        # Pull the answer from the last *AI* message that actually has text.
        # Never fall back to the human/tool message — otherwise a turn that
        # errors on its first model call would echo the user's question.
        answer = ""
        for m in reversed((final_state or {}).get("messages", []) or []):
            if getattr(m, "type", None) != "ai":
                continue
            content = m.content
            if isinstance(content, list):  # Gemini returns list-of-parts
                text = "".join(p.get("text", "") for p in content if isinstance(p, dict))
            else:
                text = content or ""
            if text.strip():
                answer = text
                break

        if not answer and err is not None:
            answer = _friendly_error(err)

        steps_md, sources, changed_files = _collect_details(final_state, answer, prev_files)
        msg = {
            "role": "assistant",
            "content": answer or "_(no text response)_",
            "sources": sources,
            "steps": steps_md,
            "files": changed_files,
        }
        _render_assistant(msg)
        st.session_state.messages.append(msg)

        if final_state:
            st.session_state.last_files = final_state.get("files", {}) or {}
            st.session_state.last_todos = final_state.get("todos", []) or []


# ---------------------------------------------------------------------------
# Main pane — tabs
# ---------------------------------------------------------------------------
tab_chat, tab_files, tab_plan = st.tabs(["💬  Chat", "📁  Files", "📝  Plan"])

with tab_chat:
    # Welcome screen + suggestion chips when the chat is empty.
    if not st.session_state.messages:
        welcome()
        c1, c2 = st.columns(2)
        for i, (label, text) in enumerate(SUGGESTIONS):
            col = c1 if i % 2 == 0 else c2
            if col.button(f"{label}\n\n{text}", key=f"sugg_{i}"):
                st.session_state.pending = text
                st.rerun()

    # All conversation (history + the live turn) renders into this container,
    # which is declared BEFORE st.chat_input so the agent's thinking/loading
    # status and its response always appear ABOVE the input box, not below it.
    chat_area = st.container()

    # Replay history.
    with chat_area:
        for m in st.session_state.messages:
            if m["role"] == "user":
                with st.chat_message("user", avatar=USER_AVATAR):
                    st.markdown(m["content"])
            else:
                with st.chat_message("assistant", avatar=BOT_AVATAR):
                    _render_assistant(m)

    # Handle a queued suggestion, then a typed prompt.
    typed = st.chat_input("Message DeepAgent…")
    prompt = st.session_state.pending or typed
    st.session_state.pending = None
    if prompt:
        with chat_area:
            run_turn(prompt)
        st.rerun()


with tab_files:
    st.subheader("🗂️ Virtual filesystem")
    st.caption("Files the agent has written this session (skills, notes, drafts).")
    files = st.session_state.last_files
    if not files:
        st.info("No files yet. Ask the agent to write or read a file.")
    else:
        for path in sorted(files):
            data = files[path]
            content = data.get("content", data) if isinstance(data, dict) else data
            if isinstance(content, list):
                content = "\n".join(content)
            with st.expander(f"📄 {path}"):
                st.code(str(content)[:5000], language="markdown")

    out_dir = os.path.join(os.path.dirname(__file__), "outputs")
    if os.path.isdir(out_dir):
        xlsx = [f for f in os.listdir(out_dir) if f.endswith(".xlsx")]
        if xlsx:
            st.divider()
            st.subheader("📊 Generated Excel files")
            for f in xlsx:
                with open(os.path.join(out_dir, f), "rb") as fh:
                    st.download_button(f"⬇️ {f}", fh.read(), file_name=f, key=f"dl_{f}")


with tab_plan:
    st.subheader("🧭 Planning todos")
    st.caption("The agent's write_todos plan for the current task.")
    todos = st.session_state.last_todos
    if not todos:
        st.info("No todos yet. Give the agent a multi-step task.")
    else:
        marks = {"completed": "✅", "in_progress": "🔄", "pending": "⬜"}
        done = sum(1 for t in todos if t.get("status") == "completed")
        st.progress(done / max(len(todos), 1), text=f"{done}/{len(todos)} completed")
        for t in todos:
            st.write(f"{marks.get(t.get('status', 'pending'), '⬜')} {t.get('content', t)}")
