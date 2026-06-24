# Skill: Report Writing

> Loaded into the deep agent's context whenever it produces a final answer. This
> skill defines how the agent turns its work into a clear, structured, durable
> written report. Read this first, then `instruction.md` for the procedure and
> `example.md` for filled-in templates.

## Purpose

This skill ensures that **whenever the deep agent answers a query**, it also
produces a well-structured report capturing the question, the approach, the
findings, and the conclusion. The report is the durable artifact of the agent's
work: it should stand on its own without the surrounding conversation, be
scannable, and be backed by specifics and sources.

A deep agent does long-horizon, multi-step work and delegates to sub-agents.
Much of that work is ephemeral. The report is where that effort is **captured,
made verifiable, and handed off** — to the user, to a later step, or to another
agent.

## When to use this skill

- **Always**, when delivering a final answer to a user query — especially for
  research, analysis, comparison, investigation, or multi-step build tasks.
- After a delegated sub-agent completes work whose result should be persisted.
- Whenever the user explicitly asks for a report, summary, brief, or write-up.

For a trivial one-line factual answer, a full report is overkill — produce a
**minimal report** (Title, Summary, Conclusion, Sources) instead of skipping it.

## Anatomy of a good report

| Section | Purpose | Required? |
|---|---|---|
| **Title** | Names what the query was about. | Always |
| **Summary / TL;DR** | Answers the question in 2–4 sentences, up front. | Always |
| **Context** | The original question, scope, and stated assumptions. | Usually |
| **Approach / Method** | Steps, tools, and sub-agents used to reach the answer. | For multi-step work |
| **Findings** | The substantive results — specific, organized, sourced. | Usually |
| **Conclusion / Recommendation** | The direct answer and next steps. | Always |
| **Risks / Limitations** | Uncertainty, caveats, what wasn't checked. | When relevant |
| **Sources / Artifacts** | Where supporting data lives (files, links, code). | When any exist |

## Core principles

1. **Answer first (BLUF — bottom line up front).** Lead with the conclusion; put
   supporting detail below. A reader should get the answer from the Summary
   alone.
2. **Be specific.** Cite numbers, names, versions, file paths, dates, and
   sources. Replace "improves performance" with "reduces p95 latency from 800ms
   to 120ms."
3. **Structure for scanning.** Use headings, short paragraphs, bullet lists, and
   tables. Assume the reader skims first.
4. **Separate fact from inference.** Mark assumptions, estimates, and
   uncertainty explicitly. Don't present a guess as a measured result.
5. **Show your sources.** Every non-obvious claim should be traceable to a
   source, a file, or a computation. Never invent citations or data.
6. **Right-size it.** Match length and depth to the task. Don't pad a simple
   answer; don't compress a complex investigation into two lines.
7. **Persist it.** Write the report to the virtual file system so it survives
   across steps and hand-offs.

## Output format & conventions

- Write in **Markdown**.
- Default location/filename: `reports/<short-kebab-case-topic>.md`
  (e.g. `reports/python-web-framework-choice.md`).
- Include a date and, if useful, the originating query verbatim in Context.
- Use tables for comparisons, code blocks for code/commands, and links/paths for
  sources.
- Keep the Summary and Conclusion present even in the shortest report.

## Tone & quality bar

- Neutral, precise, and confident where the evidence supports it; hedged where
  it doesn't.
- No filler, no marketing language, no repetition of the prompt.
- Consistent: the Conclusion must follow from the Findings; the Summary must
  match the Conclusion.

## Companion files

- `instruction.md` — the step-by-step procedure for assembling, quality-checking,
  persisting, and delivering a report.
- `example.md` — filled-in templates: a full research report, a short-answer
  report, and a technical-investigation report.
