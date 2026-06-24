"""Presentation layer: modern CSS theme + small render helpers for app.py."""
from __future__ import annotations

import streamlit as st

# Emoji avatars used for chat bubbles.
USER_AVATAR = "🧑‍💻"
BOT_AVATAR = "🤖"

CSS = """
<style>
/* ---- Base / typography -------------------------------------------------- */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"]  { font-family: 'Inter', sans-serif; }

.block-container { padding-top: 1.2rem; padding-bottom: 7rem; max-width: 950px; }

/* Hide default Streamlit chrome for a cleaner app feel */
#MainMenu, footer, header [data-testid="stToolbar"] { visibility: hidden; }

/* ---- Hero header -------------------------------------------------------- */
.hero {
    background: linear-gradient(120deg, #7C5CFF 0%, #5B8DEF 55%, #18C8B6 100%);
    border-radius: 20px;
    padding: 22px 26px;
    margin-bottom: 14px;
    box-shadow: 0 10px 30px rgba(124, 92, 255, 0.25);
}
.hero h1 { color: #fff; font-size: 1.6rem; font-weight: 700; margin: 0; letter-spacing:-0.5px;}
.hero p  { color: rgba(255,255,255,0.92); margin: 4px 0 0; font-size: 0.92rem; }

/* capability pills inside hero */
.pills { margin-top: 12px; display:flex; flex-wrap:wrap; gap:7px; }
.pill {
    background: rgba(255,255,255,0.16);
    color:#fff; border:1px solid rgba(255,255,255,0.25);
    padding: 3px 11px; border-radius: 999px; font-size: 0.74rem; font-weight:500;
    backdrop-filter: blur(6px);
}

/* ---- Chat messages ------------------------------------------------------ */
[data-testid="stChatMessage"] {
    background: transparent;
    padding: 6px 0;
    gap: 14px;
}

/* ASSISTANT reply = clean, full-width "document" card (Claude / ChatGPT style),
   NOT a cramped chat bubble. */
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) [data-testid="stChatMessageContent"] {
    background: #141925;
    border: 1px solid #232B3D;
    border-radius: 14px;
    padding: 18px 22px;
    box-shadow: 0 4px 18px rgba(0,0,0,0.22);
    max-width: 100%;
    width: 100%;
}

/* user message -> flip to the right + accent gradient */
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
    flex-direction: row-reverse;
    text-align: left;
}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) [data-testid="stChatMessageContent"] {
    background: linear-gradient(135deg, #7C5CFF, #5B8DEF);
    border: none;
    color: #fff;
    border-radius: 16px 16px 4px 16px;
    margin-left: auto;
}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) [data-testid="stChatMessageContent"] p { color:#fff; }

/* ---- Rich markdown formatting inside assistant document card ------------ */
[data-testid="stChatMessageContent"] p {
    line-height: 1.75; font-size: 0.98rem; color:#E2E7F0; margin: 0 0 0.95em;
}
[data-testid="stChatMessageContent"] p:last-child { margin-bottom: 0; }

[data-testid="stChatMessageContent"] h1,
[data-testid="stChatMessageContent"] h2,
[data-testid="stChatMessageContent"] h3,
[data-testid="stChatMessageContent"] h4 {
    color:#F4F6FB; font-weight:700; line-height:1.3;
    margin: 1.5em 0 0.55em; letter-spacing:-0.3px;
}
[data-testid="stChatMessageContent"] h1 { font-size:1.6rem; }
[data-testid="stChatMessageContent"] h2 {
    font-size:1.3rem; padding-bottom:0.32em; border-bottom:1px solid #2A3142;
}
[data-testid="stChatMessageContent"] h3 { font-size:1.12rem; color:#C0B2FF; }
[data-testid="stChatMessageContent"] h4 { font-size:1.0rem; color:#A6BAEC; }
[data-testid="stChatMessageContent"] > :first-child { margin-top: 0; }

/* lists */
[data-testid="stChatMessageContent"] ul,
[data-testid="stChatMessageContent"] ol { margin: 0.4em 0 1em; padding-left: 1.5em; }
[data-testid="stChatMessageContent"] li { margin: 0.4em 0; line-height:1.7; color:#E2E7F0; }
[data-testid="stChatMessageContent"] li::marker { color:#8B6CFF; font-weight:700; }
[data-testid="stChatMessageContent"] li > ul,
[data-testid="stChatMessageContent"] li > ol { margin: 0.3em 0; }

/* inline code */
[data-testid="stChatMessageContent"] code {
    background:#0E1320; color:#7CE7C4; border:1px solid #232B3D;
    padding: 1px 6px; border-radius:6px; font-size:0.84em;
    font-family: 'JetBrains Mono','SFMono-Regular',Consolas,monospace;
}
/* code blocks */
[data-testid="stChatMessageContent"] pre {
    background:#0C111C !important; border:1px solid #232B3D;
    border-radius:12px; padding:14px 16px; margin:0.7em 0; overflow-x:auto;
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.03);
}
[data-testid="stChatMessageContent"] pre code {
    background:transparent; border:none; padding:0; color:#D6DEEC; font-size:0.83rem; line-height:1.55;
}

/* tables */
[data-testid="stChatMessageContent"] table {
    border-collapse:collapse; width:100%; margin:0.7em 0; font-size:0.86rem;
    border-radius:10px; overflow:hidden; border:1px solid #2A3142;
}
[data-testid="stChatMessageContent"] th {
    background:#222A3C; color:#EAEDF4; font-weight:600; text-align:left;
    padding:8px 12px; border-bottom:1px solid #2A3142;
}
[data-testid="stChatMessageContent"] td {
    padding:8px 12px; border-bottom:1px solid #1F2636; color:#DDE2EC;
}
[data-testid="stChatMessageContent"] tr:nth-child(even) td { background:#161B28; }
[data-testid="stChatMessageContent"] tr:last-child td { border-bottom:none; }

/* blockquotes */
[data-testid="stChatMessageContent"] blockquote {
    border-left:3px solid #7C5CFF; background:#141926;
    margin:0.7em 0; padding:8px 14px; border-radius:0 10px 10px 0; color:#B9C2D6;
}
/* links */
[data-testid="stChatMessageContent"] a { color:#7CB8FF; text-decoration:none; border-bottom:1px solid rgba(124,184,255,0.35); }
[data-testid="stChatMessageContent"] a:hover { border-bottom-color:#7CB8FF; }
/* horizontal rule */
[data-testid="stChatMessageContent"] hr { border:none; border-top:1px solid #2A3142; margin:1em 0; }
/* user bubble keeps everything white */
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) [data-testid="stChatMessageContent"] * { color:#fff !important; }

/* avatars */
[data-testid="stChatMessageAvatarUser"],
[data-testid="stChatMessageAvatarAssistant"] {
    width: 36px; height: 36px; border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.25);
}

/* ---- Welcome card + suggestion chips ------------------------------------ */
.welcome {
    text-align:center; padding: 26px 10px 6px; color:#A8B0C2;
}
.welcome .big { font-size: 2.6rem; }
.welcome h3 { color:#E8EAF0; margin:8px 0 2px; font-weight:600; }
.welcome p { font-size:0.9rem; margin:0; }

div[data-testid="column"] .stButton > button {
    width:100%; text-align:left; white-space:normal;
    background:#161A24; border:1px solid #262C3D; border-radius:14px;
    padding:12px 14px; color:#C7CEDC; font-size:0.84rem; font-weight:500;
    transition: all .15s ease; min-height: 64px;
}
div[data-testid="column"] .stButton > button:hover {
    border-color:#7C5CFF; background:#1B2030; color:#fff;
    transform: translateY(-2px); box-shadow:0 6px 18px rgba(124,92,255,0.18);
}

/* ---- Chat input --------------------------------------------------------- */
[data-testid="stChatInput"] {
    border-radius: 16px; border:1px solid #2A3142; background:#161A24;
}
[data-testid="stChatInput"]:focus-within { border-color:#7C5CFF; box-shadow:0 0 0 3px rgba(124,92,255,0.18); }

/* ---- Sidebar ------------------------------------------------------------ */
[data-testid="stSidebar"] { background:#0B0E16; border-right:1px solid #1C2230; }
[data-testid="stSidebar"] .stToggle { padding:1px 0; }
.side-title {
    font-size:1.15rem; font-weight:700; color:#fff; margin-bottom:2px;
    display:flex; align-items:center; gap:8px;
}
.side-sub { color:#8A93A6; font-size:0.78rem; margin-bottom:10px; }
.section-label {
    text-transform:uppercase; letter-spacing:0.6px; font-size:0.68rem;
    color:#6E7689; font-weight:700; margin:14px 0 4px;
}
.keyrow { font-size:0.8rem; color:#C7CEDC; padding:1px 0; }

/* tabs */
.stTabs [data-baseweb="tab-list"] { gap:4px; }
.stTabs [data-baseweb="tab"] {
    border-radius:10px 10px 0 0; padding:6px 14px; font-size:0.85rem;
}
/* per-response sub-tabs inside the assistant card */
[data-testid="stChatMessageContent"] .stTabs [data-baseweb="tab-list"] {
    border-bottom:1px solid #232B3D; margin-bottom:4px;
}
[data-testid="stChatMessageContent"] .stTabs [aria-selected="true"] {
    color:#C0B2FF; border-bottom:2px solid #8B6CFF;
}
[data-testid="stChatMessageContent"] .stTabs [data-baseweb="tab-panel"] { padding-top:14px; }

/* status box */
[data-testid="stStatusWidget"], div[data-testid="stExpander"] details {
    border-radius:12px; border-color:#262C3D;
}
</style>
"""


def inject_css() -> None:
    st.markdown(CSS, unsafe_allow_html=True)


def hero(active_pills: list[str]) -> None:
    pills = "".join(f'<span class="pill">{p}</span>' for p in active_pills)
    st.markdown(
        f"""
        <div class="hero">
            <h1>🤖 DeepAgent Chat</h1>
            <p>A conversational deep agent — planning, skills, subagents, web
            search & a virtual filesystem, all in one chat.</p>
            <div class="pills">{pills}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def welcome() -> None:
    st.markdown(
        """
        <div class="welcome">
            <div class="big">💬</div>
            <h3>Start a conversation</h3>
            <p>Ask anything, or try one of the ideas below — each shows off a deep-agent feature.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
