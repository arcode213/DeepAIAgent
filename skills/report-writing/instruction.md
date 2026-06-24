# Instructions: Report Writing Skill

The procedure the deep agent follows to turn its work into a written report.
Apply this **whenever delivering a final answer**.

---

## Phase 1 — Gather the material

- Collect: the original query, the steps taken, tool outputs, sub-agent
  conclusions, and any artifacts already written to the file system.
- Identify the **single most important takeaway** — this becomes the Summary.
- List the supporting evidence and where each piece came from (so it can be
  cited).
- Note any assumptions made and any parts of the question left unanswered.

## Phase 2 — Decide the report's scope

Choose the shape based on the task:

- **Minimal report** (trivial factual answer): Title, Summary, Conclusion,
  Sources.
- **Standard report** (analysis/comparison/build): add Context, Approach,
  Findings.
- **Full report** (research/investigation): add Risks/Limitations and a richer
  Findings section with sub-headings.

Do not pad. A two-line question does not become five sections.

## Phase 3 — Draft the report

Assemble the sections in this order, but **write the Summary last**, after the
findings are settled, so it accurately reflects them:

1. **Title** — what the query was about, as a noun phrase.
2. **Context** — the question (quote it if helpful), scope, and assumptions.
3. **Approach / Method** — the steps, tools, and sub-agents used. Keep it brief;
   this is about credibility/reproducibility, not narration.
4. **Findings** — the substance:
   - Organize with sub-headings or a logical order.
   - Use **tables for comparisons**, lists for enumerations, code blocks for
     code/commands/config.
   - Attach a source to every non-obvious claim.
   - Distinguish measured facts from inferences and estimates.
5. **Risks / Limitations** — caveats, uncertainty, what wasn't verified.
6. **Conclusion / Recommendation** — the direct answer and concrete next steps.
7. **Sources / Artifacts** — files, links, code references, datasets.
8. **Summary / TL;DR** — write it now; place it at the top. 2–4 sentences that
   answer the question on their own.

## Phase 4 — Quality check (self-review)

- [ ] Does the **Summary alone** answer the user's question? (It must.)
- [ ] Is every claim **specific** (numbers, names, versions, dates) and, where
      relevant, **sourced**?
- [ ] Are assumptions, estimates, and uncertainty clearly labeled?
- [ ] Does the **Conclusion follow from the Findings**? Do Summary and
      Conclusion agree?
- [ ] Is it **scannable** (headings, short paragraphs, lists/tables)?
- [ ] Is the **length right** for the question's complexity?
- [ ] No invented data or sources; no unstated leaps.

## Phase 5 — Persist and deliver

- Write the report to the file system as `reports/<short-kebab-case-topic>.md`.
- Present the **Summary inline** to the user and tell them where the full report
  was saved (`file:path`).
- If the report is part of a larger task, note that it's available for later
  steps or sub-agents, and link related artifacts.

---

## Adapting the template by report type

- **Comparison / decision** → lead with the recommendation; use a criteria
  table; add a short "why not the alternatives" note.
- **Research / literature** → emphasize Sources; separate well-supported claims
  from contested ones; date the information.
- **Technical investigation / debugging** → Findings becomes
  "Symptom → Root cause → Evidence → Fix"; include reproduction steps.
- **Build / implementation** → Findings becomes "What changed (file:line) →
  Why → How verified"; include how to run/test it.
- **Status / progress** → "Done / In progress / Blocked / Next" with owners and
  dates.

## Guardrails

- **Never invent** data, numbers, quotes, or sources. If something is unknown,
  say "unknown" or "not verified."
- Keep the **Conclusion consistent** with the Findings; don't overstate
  certainty or generalize beyond the evidence.
- Preserve any **citations/sources** produced by research sub-agents — don't
  drop attribution.
- Convert relative dates to absolute ones (e.g. "today" → the actual date) so
  the report stays correct over time.
- Match length and depth to the query; resist the urge to pad.
