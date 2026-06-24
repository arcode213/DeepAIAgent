"""Tools used by the Deep Agent chatbot.

These mirror the tools demonstrated across the deepagentsdemo notebooks:
 - `web_search`     -> Tavily internet search (notebooks 1, 2, 6)
 - `save_to_excel`  -> structured-data extraction to an .xlsx file (notebook 2)
"""
from __future__ import annotations

import os
from typing import Literal

import pandas as pd
from langchain_core.tools import tool
from tavily import TavilyClient


def _tavily() -> TavilyClient:
    """Lazily build a Tavily client so the app can start without the key set."""
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        raise RuntimeError(
            "TAVILY_API_KEY is not set. Add it to your .env to enable web search."
        )
    return TavilyClient(api_key=api_key)


@tool
def web_search(
    query: str,
    max_results: int = 5,
    topic: Literal["general", "news", "finance"] = "general",
    include_raw_content: bool = False,
):
    """Search the web with Tavily for the given query and return the results.

    Use this whenever the user needs up-to-date facts, sources, or research that
    is not in your training data.
    """
    return _tavily().search(
        query=query,
        max_results=max_results,
        topic=topic,
        include_raw_content=include_raw_content,
    )


# ---- Excel extraction tool (from 2-traveldatadeepagent.ipynb) ----------------
# Canonical output columns and the aliases the model might use for each.
_COLUMNS = ["Name", "City", "Email", "Contact"]
_ALIASES = {
    "Name": ["Name", "Agency Name", "TAgency Name", "Company", "Title", "Agency"],
    "City": ["City", "City Of Operate", "Cities", "Location", "City Of Operation"],
    "Email": ["Email", "Emailaddress", "Email Address", "E-mail", "Emails"],
    "Contact": ["Contact", "Phone", "Phone Number", "Contact Number", "Telephone", "Number"],
}


@tool
def save_to_excel(data: list[dict], filename: str = "extracted_data.xlsx"):
    """Save a list of dictionaries (rows) to an Excel file.

    Each dict describes one record with name/city/email/contact-style fields.
    Common key spellings are accepted (e.g. 'Name', 'Agency Name', 'Email',
    'Phone'). Rows are de-duplicated by Name. Call this ONCE with the full list.
    Returns the path to the saved file.
    """
    rows = []
    for item in data or []:
        if not isinstance(item, dict):
            continue
        norm = {}
        for canonical, aliases in _ALIASES.items():
            value = ""
            for a in aliases:
                if a in item and str(item[a]).strip() not in ("", "nan", "None"):
                    value = item[a]
                    break
            if value == "":
                lowered = [a.lower() for a in aliases]
                for k, v in item.items():
                    if k.strip().lower() in lowered and str(v).strip():
                        value = v
                        break
            norm[canonical] = value
        rows.append(norm)

    df = pd.DataFrame(rows, columns=_COLUMNS).fillna("")
    df = df[df["Name"].astype(str).str.strip() != ""]
    df = df.drop_duplicates(subset=["Name"], keep="first").reset_index(drop=True)

    out_dir = os.path.join(os.path.dirname(__file__), "outputs")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, filename)
    df.to_excel(path, index=False)
    return f"Saved {len(df)} rows to {path}"
