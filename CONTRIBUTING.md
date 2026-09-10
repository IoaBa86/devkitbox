# Contributing to DevKitBox

## Development setup

Requires Python 3.12+ (developed against 3.13) on Windows.

```powershell
py -3.13 -m venv .venv
.venv\Scripts\pip install -e ".[dev]"
```

Run the app:

```powershell
.venv\Scripts\python -m app.main
```

Run tests:

```powershell
.venv\Scripts\python -m pytest
```

Lint and format:

```powershell
.venv\Scripts\python -m ruff check .
.venv\Scripts\python -m ruff format .
```

All four must pass before a change is considered done.

## Project structure

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — in particular, the
"Anatomy of a tool" section if you're adding or changing a tool.

## Code style

- Ruff is the source of truth (`E`, `F`, `I`, `UP`, `B`, `SIM` rule sets are
  enabled in `pyproject.toml`); run it before opening a PR.
- Tool logic (`logic.py`) stays free of Qt imports and is unit-tested
  directly. Qt code lives only in `widget.py`.
- No unnecessary comments — code should read clearly from names and
  structure; comments are for non-obvious *why*, not *what*.
- Don't add abstractions, config flags, or generalization for hypothetical
  future needs. Match the existing pattern for the layer you're touching
  rather than introducing a new one.

## Tests

Every tool needs both:

- `tests/unit/test_<name>_logic.py` — pure logic, no Qt.
- A widget-level smoke test in `tests/integration/` exercising the real
  button/signal wiring, not just the underlying function. This project has
  caught real bugs this way that logic-only tests missed entirely (a
  table row too short to show its own text; a mode toggle that hid a
  value label but left its field-name label stranded).

## Commit messages

Plain, descriptive, present tense (`Add cron expression explainer`, `Fix
QR code overflow at high error correction`). No trailers beyond a normal
`Signed-off-by` if your workflow uses one.

## Pull requests

Not currently accepting external contributions — this file exists for
whoever ends up working on this codebase (including future-you).
