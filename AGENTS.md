# Repository Guidelines

## Project Structure & Module Organization
- `spec.md` holds the UX/behavior contract for `jail`.
- Python layout (planned):
  - `src/jail/cli.py` – Typer CLI entrypoint.
  - `src/jail/runtime/` – devcontainer orchestration (v1 focus).
  - `src/jail/templates/.devcontainer/` – scaffolds for `jail init`.
  - `tests/` – pytest unit/integration suites.
  - `docs/` – additional docs and examples.

## Build, Test, and Development Commands
- Setup (uv preferred): `uv sync` then `uv run jail --help`.
- Lint/format: `uv run ruff check .` | `uv run black .` | `uv run isort .`.
- Type check: `uv run mypy src`.
- Unit tests: `uv run pytest -q`.
- Integration (Dev Containers CLI + Docker required): `uv run pytest -q -m integration`.
- Alt (without uv): `pip install -e .[dev]` then run the same tools.

## Coding Style & Naming Conventions
- Language: Python 3.11+; PEP 8 with Black formatting.
- Indentation 4 spaces; line length 100.
- Names: packages/modules `snake_case`; classes `PascalCase`; functions/vars `snake_case`.
- Use type hints; validate JSON via Pydantic or `jsonschema`.

## Testing Guidelines
- Framework: pytest; tests in `tests/` with names like `test_init.py`, `test_codex.py`.
- Mark Docker-dependent tests `@pytest.mark.integration`; keep unit tests fast and hermetic.
- Target coverage ≥85% on core modules; run `uv run pytest --cov=src -q`.

## Commit & Pull Request Guidelines
- Conventional Commits: `feat:`, `fix:`, `docs:`, `refactor:`, `chore:`, `test:`, `ci:`.
- Update `spec.md` with any behavior/flag changes; include `--help`/`--dry-run` output in PRs.
- Link issues, describe risks, and note security implications of container changes.

## Architecture & Runtime Choices
- V1 scope: devcontainers only. We require the Dev Containers CLI (`devcontainer`) and Docker; execution is driven by the devcontainer spec. No pure-Docker runner in v1.
- Rationale: the devcontainer spec ensures editor parity and predictable UX across hosts.
- Future: we may explore a Docker-only workflow later if it meaningfully simplifies CI or reduces dependencies.

## Security & Configuration Tips
- Propagate only `~/.codex` read-only when requested; never mount other host secrets.
- Run as non-root; confine “dangerous” operations to the container; honor `--dry-run`/`--non-interactive`.
- Telemetry stays off unless `JAIL_TELEMETRY=1`.
