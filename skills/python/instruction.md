# Instructions: Python Skill

The operating procedure the deep agent follows for any Python task. Work through
the phases in order; skip phases only when the task is trivially small, and say
so when you do.

---

## Phase 1 — Understand the requirement

- Restate the goal in one sentence. Identify **inputs, outputs, constraints,
  and the success criterion.**
- Determine the runtime context: Python version, OS, whether it runs as a
  script, library, service, notebook cell, or CLI.
- Inspect the existing project **before writing anything**:
  - `pyproject.toml` / `requirements.txt` / `setup.py` → dependencies & version.
  - `.python-version` / `tox.ini` / CI config → supported versions.
  - Existing modules → conventions, style, and patterns to match.
- List edge cases up front: empty input, large input, malformed data, missing
  files, network failures, concurrency, unicode, timezones.
- If a requirement is genuinely ambiguous and the choice is irreversible, state
  the assumption explicitly or ask. Otherwise pick the sensible default and note
  it.

## Phase 2 — Set up the environment (when starting fresh)

- Prefer the tool the repo already uses. For a new project:
  - `uv init` / `uv venv` then `uv add <deps>`, **or** `python -m venv .venv` +
    `pip install`.
  - Declare metadata and deps in `pyproject.toml` (PEP 621).
- Pin or respect existing dependency versions; never silently upgrade a pinned
  dependency to make something work — flag it instead.
- Add dev tooling consistent with the repo: `ruff`, `mypy`/`pyright`, `pytest`.

## Phase 3 — Design before coding

- For multi-step work, write the plan to the planning tool / TODO list first.
- Decide the module/function boundaries. Aim for:
  - Small functions with a single responsibility.
  - A **pure core** (logic) separated from the **imperative shell** (I/O).
  - Clear data structures (`dataclass`, `Enum`, `TypedDict`, `pydantic`) for
    anything with more than two related fields.
- Choose stdlib over third-party where it suffices.
- Sketch the public API (signatures + types) before filling in bodies.

## Phase 4 — Write the code

Follow these rules:

- **Signatures first.** Write type-annotated signatures and a docstring stating
  behavior, args, returns, and what is raised.
- **Validate at the boundary.** Check inputs early; raise specific exceptions
  (`ValueError`, `TypeError`, custom exceptions) with messages that say what was
  wrong and what was expected.
- **Use the right constructs:**
  - `pathlib.Path` for filesystem paths; never string-concatenate paths.
  - Context managers (`with`) for files, locks, connections.
  - f-strings for formatting; `logging` (not `print`) for library/service
    diagnostics.
  - Comprehensions/generators for transforms; `itertools`/`functools` for
    common patterns.
- **Avoid the anti-patterns** in `skill.md` (mutable defaults, bare except,
  `shell=True`, wildcard imports, shadowing built-ins).
- **Concurrency:** use `asyncio` for I/O-bound work, `concurrent.futures` /
  `multiprocessing` for CPU-bound. Don't share mutable state without locks.
- **Match surrounding style** when editing existing files (naming, imports,
  comment density, quote style).

## Phase 5 — Handle errors deliberately

- Catch the **specific** exception you expect, at the level that can do
  something about it. Let unexpected exceptions propagate.
- Use `raise ... from err` to preserve the cause chain.
- Define a small custom exception hierarchy for a library's own error domain.
- Never `except: pass`. If you must suppress, use `contextlib.suppress(Specific)`
  and document why.
- Clean up resources with `with` or `try/finally`.

## Phase 6 — Test

- Add or update `pytest` tests for all non-trivial logic.
- Cover: the happy path, boundary values, and each error path.
- Use fixtures (`tmp_path`, `monkeypatch`, `capsys`), `@pytest.mark.parametrize`
  for table-driven cases, and `pytest.raises` for error assertions.
- Keep tests fast and deterministic; mock network/time/randomness.
- Aim for meaningful coverage of behavior, not a coverage-percentage target.

## Phase 7 — Verify for real

- Run the linter and formatter (`ruff check`, `ruff format --check`).
- Run the type checker if configured (`mypy` / `pyright`).
- Run the tests (`pytest`) or execute the script on a representative input.
- **Report the actual result.** Never claim it works without running it. If a
  step was skipped (e.g. no test runner available), say so.

## Phase 8 — Review checklist (self-review before reporting)

- [ ] Public functions are typed and documented.
- [ ] Inputs validated; specific exceptions raised with clear messages.
- [ ] No mutable defaults, bare except, `shell=True`, or shadowed built-ins.
- [ ] Resources managed with `with`/`finally`.
- [ ] Logic is testable (side effects isolated); tests exist and pass.
- [ ] Names are clear; functions are small; nesting is shallow.
- [ ] No needless dependency added; stdlib used where it suffices.
- [ ] Performance is reasonable for the expected input size (no accidental
      O(n²), no loading huge files fully into memory when streaming works).

## Phase 9 — Report

- Summarize what changed, **where (`file:line`)**, and why.
- State assumptions, limitations, and any follow-ups.
- If part of a larger task, persist notes/artifacts to the file system.

---

## Performance guidance

- Measure before optimizing (`timeit`, `cProfile`, `tracemalloc`). Don't guess.
- Prefer built-in/ C-backed operations (`str.join`, comprehensions, `set`
  membership) over manual Python loops.
- Use generators to stream large data instead of building giant lists.
- Choose the right container: `set`/`dict` for membership/lookup (O(1)),
  `collections.deque` for queues, `heapq` for priority.
- Cache pure expensive calls with `functools.cache`/`lru_cache`.

## Packaging & distribution (when relevant)

- Define `[project]` metadata in `pyproject.toml`; use a `src/` layout.
- Specify `requires-python` and dependency version ranges sensibly.
- Build with `python -m build` (or `uv build`); publish with `twine`/`uv publish`.
- Provide a console entry point via `[project.scripts]` for CLIs.

## Guardrails (always)

- Never run untrusted input through `eval`/`exec`.
- Prefer `subprocess.run([...], check=True)` with an argument **list** over
  `shell=True`; validate/escape any dynamic value.
- Keep secrets in environment variables or a secrets manager — never in source.
- Don't catch bare exceptions; don't silence errors.
- Respect existing dependency pins and project conventions.
