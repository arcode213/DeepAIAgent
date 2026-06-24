# Examples: Python Skill

Worked examples demonstrating the expected output style: typing, validation,
docstrings, error handling, tests, and idiomatic constructs. Use these as
templates for structure and quality.

---

## Example 1 — A small, typed, tested utility

**Task:** "Read a CSV of transactions and return total spend per category."

```python
from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path


def spend_by_category(csv_path: str | Path) -> dict[str, float]:
    """Return total spend per category from a transactions CSV.

    The CSV must have headers ``category`` and ``amount``.

    Args:
        csv_path: Path to the CSV file.

    Returns:
        Mapping of category name to total spend.

    Raises:
        FileNotFoundError: if the path does not exist.
        ValueError: if a required column is missing or an amount is invalid.
    """
    path = Path(csv_path)
    if not path.exists():
        raise FileNotFoundError(f"No such file: {path}")

    totals: dict[str, float] = defaultdict(float)
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for line_no, row in enumerate(reader, start=2):  # line 1 is the header
            try:
                category = row["category"].strip()
                amount = float(row["amount"])
            except (KeyError, ValueError) as exc:
                raise ValueError(f"Bad row at line {line_no}: {exc}") from exc
            totals[category] += amount

    return dict(totals)
```

**Tests:**

```python
import textwrap
import pytest
from mymodule import spend_by_category


def test_spend_by_category(tmp_path):
    csv_file = tmp_path / "tx.csv"
    csv_file.write_text(textwrap.dedent("""\
        category,amount
        food,10.50
        food,4.50
        travel,30
    """))
    assert spend_by_category(csv_file) == {"food": 15.0, "travel": 30.0}


def test_missing_file():
    with pytest.raises(FileNotFoundError):
        spend_by_category("does_not_exist.csv")


@pytest.mark.parametrize("bad", ["category,amount\nfood,abc\n", "wrong,header\n"])
def test_bad_rows_raise(tmp_path, bad):
    f = tmp_path / "bad.csv"
    f.write_text(bad)
    with pytest.raises(ValueError):
        spend_by_category(f)
```

---

## Example 2 — A dataclass modeling domain data

```python
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Priority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass(frozen=True, slots=True)
class Task:
    """An immutable unit of work."""

    title: str
    priority: Priority = Priority.MEDIUM
    tags: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not self.title.strip():
            raise ValueError("title must not be empty")

    def is_urgent(self) -> bool:
        return self.priority is Priority.HIGH
```

Notes: `frozen=True` makes instances hashable/immutable; `slots=True` saves
memory; `Enum` makes priority values a closed set; `__post_init__` validates.

---

## Example 3 — Safe subprocess call

```python
import subprocess


def git_current_branch() -> str:
    """Return the current git branch name."""
    result = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        capture_output=True,
        text=True,
        check=True,            # raises CalledProcessError on non-zero exit
    )
    return result.stdout.strip()
```

A **list** of args (no `shell=True`) avoids shell-injection. `check=True` turns
failures into exceptions instead of silent bad data.

---

## Example 4 — Async I/O-bound concurrency

```python
import asyncio
import httpx


async def fetch_status(client: httpx.AsyncClient, url: str) -> tuple[str, int]:
    """Return (url, HTTP status) for one request."""
    resp = await client.get(url, timeout=10.0)
    return url, resp.status_code


async def fetch_all(urls: list[str]) -> dict[str, int]:
    """Fetch many URLs concurrently and return their status codes."""
    async with httpx.AsyncClient() as client:
        tasks = [fetch_status(client, u) for u in urls]
        results = await asyncio.gather(*tasks, return_exceptions=False)
    return dict(results)


# asyncio.run(fetch_all(["https://example.com", "https://python.org"]))
```

Use `asyncio` for I/O-bound fan-out. For CPU-bound work use
`concurrent.futures.ProcessPoolExecutor` instead (the GIL limits threads).

---

## Example 5 — A small CLI with argparse

```python
from __future__ import annotations

import argparse
import sys
from pathlib import Path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Summarize spend by category.")
    parser.add_argument("csv", type=Path, help="Path to transactions CSV")
    parser.add_argument("--top", type=int, default=5, help="Show top N categories")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        totals = spend_by_category(args.csv)
    except (FileNotFoundError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    for category, amount in sorted(totals.items(), key=lambda kv: -kv[1])[: args.top]:
        print(f"{category:<15} {amount:>10.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

Returning an int exit code from `main` makes the CLI testable and shell-friendly.

---

## Example 6 — Streaming large files with a generator

```python
from collections.abc import Iterator
from pathlib import Path


def count_matching_lines(path: Path, needle: str) -> int:
    """Count lines containing ``needle`` without loading the whole file."""
    def lines() -> Iterator[str]:
        with path.open(encoding="utf-8") as f:
            yield from f

    return sum(1 for line in lines() if needle in line)
```

Streaming keeps memory flat regardless of file size.

---

## Style checklist these examples demonstrate

- Type hints on every signature and return; precise types where useful.
- Docstrings stating behavior, args, returns, and raises.
- Input validation at the boundary with specific exceptions and clear messages.
- `pathlib` for files; context managers for resources; f-strings for formatting.
- `dataclass`/`Enum` for structured, closed-set data.
- Tests covering happy path, edge cases, and error paths (parametrized).
- No `shell=True`, no bare `except`, no mutable defaults, no shadowed built-ins.
- The right concurrency model for the workload; generators for large data.
