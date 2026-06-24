# Skill: Python

> Loaded into the deep agent's context when a task involves writing, reviewing,
> debugging, or reasoning about Python code. Read this file first to decide
> relevance, then load `instruction.md` for the procedure and `example.md` for
> output style.

## Purpose

This skill makes the agent an effective, modern Python engineer. It covers the
full lifecycle: understanding a requirement, choosing the right structure,
writing idiomatic and typed code, testing it, and packaging/shipping it. Use it
for any task where Python is the implementation language or where Python
ecosystem knowledge is required to answer correctly.

## When to use this skill

Trigger on any of the following:

- Writing new Python code: scripts, modules, libraries, CLIs, services, data
  pipelines, automation/glue code.
- Modifying existing Python: refactor, bug fix, feature add, performance tuning.
- Reviewing Python for correctness, readability, security, or performance.
- Explaining Python behavior, semantics, or ecosystem choices.
- Setting up a Python project: dependencies, virtual environments, linting,
  type checking, test harness, packaging.
- Debugging tracebacks, import errors, dependency conflicts, or runtime failures.

Do **not** reach for this skill when the project is clearly another language;
check `pyproject.toml` / `requirements.txt` / file extensions first.

## Target environment & versions

- **Assume Python 3.10+ unless the project says otherwise.** Confirm the version
  from `pyproject.toml` (`requires-python`), `.python-version`, or `python
  --version` before relying on version-specific syntax.
- Modern features available by minimum version:
  - 3.10: structural pattern matching (`match`/`case`), `X | Y` union types,
    parenthesized context managers.
  - 3.11: `tomllib`, exception groups, `Self` type, faster CPython.
  - 3.12: `type` statement for aliases, improved f-string parsing, generic
    syntax for functions/classes (PEP 695).
  - 3.13: experimental free-threaded build, improved REPL.
- For libraries meant to be widely consumed, support the oldest Python still in
  common use unless told otherwise; for an app, target a single pinned version.

## The Python toolchain (defaults)

| Concern            | Default tool            | Notes                                        |
|--------------------|-------------------------|----------------------------------------------|
| Env + deps         | `uv` (or `pip`+`venv`)  | `uv` is fast; respect what the repo already uses. |
| Project metadata   | `pyproject.toml`        | PEP 621 `[project]` table.                    |
| Lint + format      | `ruff` (+ `ruff format`)| Replaces flake8/isort/black for most repos.   |
| Type check         | `mypy` or `pyright`     | Run in CI; annotate public APIs.              |
| Tests              | `pytest`                | Fixtures, parametrize, `tmp_path`, `monkeypatch`. |
| Task running       | `make` / `uv run` / `nox`/`tox` | Match the repo's convention.          |

Always **match the tools the repository already uses** rather than introducing
new ones. Detect them from config files before suggesting changes.

## What "good Python" looks like (principles)

1. **Readability first.** Code is read far more than written. Prefer clear names,
   small functions, and flat control flow (early returns over deep nesting).
2. **Type the public surface.** Annotate all function signatures, return types,
   and class attributes. Use precise types (`Sequence`, `Mapping`, `Iterable`,
   `Protocol`) over bare `list`/`dict` where it communicates intent.
3. **Fail loudly and early.** Validate inputs at boundaries; raise specific
   exceptions with actionable messages. Don't return `None` to signal errors.
4. **Pure core, imperative shell.** Keep side effects (I/O, network, printing) at
   the edges; keep business logic pure and therefore testable.
5. **Prefer the standard library.** Reach for `collections`, `itertools`,
   `functools`, `pathlib`, `dataclasses`, `enum`, `contextlib` before adding a
   dependency.
6. **Make illegal states unrepresentable.** Use `Enum`, `dataclass(frozen=True)`,
   and narrow types so bad data can't be constructed.
7. **Explicit over implicit.** No mutable default arguments, no wildcard imports,
   no relying on truthiness for `None` checks (`if x is None`, not `if not x`).
8. **Test behavior, not implementation.** Cover the happy path, edge cases, and
   error paths.

## Common anti-patterns to avoid

- Mutable default arguments (`def f(x=[])`) — use `None` + assign inside.
- Bare `except:` or `except Exception` that swallows everything silently.
- `eval`/`exec` on untrusted input; `subprocess(..., shell=True)` with user data.
- Catch-and-pass that hides errors; reassigning built-ins (`list`, `id`, `type`).
- Deeply nested code; functions doing many things; "god" modules.
- Manual resource management instead of `with`; string-concatenated file paths.
- Premature optimization, and its opposite — O(n²) loops over large data.

## Idiomatic constructs cheat sheet

- Comprehensions for simple maps/filters; generator expressions for streaming.
- `enumerate`, `zip`, `itertools` instead of index bookkeeping.
- `dataclasses` / `pydantic` for structured data; `NamedTuple` for lightweight
  immutable records.
- `pathlib.Path` for filesystem; `with` / `contextlib` for resources.
- `logging` (not `print`) for diagnostics in libraries and services.
- `functools.lru_cache` / `cache` for pure expensive functions.
- `asyncio` for I/O-bound concurrency; `concurrent.futures`/`multiprocessing`
  for CPU-bound parallelism (mind the GIL).

## Companion files

- `instruction.md` — the step-by-step operating procedure for any Python task,
  including setup, writing, testing, performance, and review checklists.
- `example.md` — worked examples (utility, class, async, CLI, data processing,
  tests) demonstrating the expected output style.
