# jail 🔒 — Safe sandboxes for AI coding agents

**Give your AI coding agents a playground where they (probably) can't break anything important.**

> ⚠️ **Experimental Software**: This is an early experiment in AI-safe development environments. We're actively exploring the best patterns for isolating AI agents. Expect breaking changes and rough edges — but also exciting possibilities!

`jail` creates isolated development containers for AI agents like Codex to run wild in — keeping your host system safe while maintaining a productive workflow. One command sets up everything you need.

```bash
# Create a safe workspace and let your AI loose
jail init "a python cli app"

# Get interactive codex from inside the jail
jail codex

# Get shell in the jail
jail
```

## Yes of course we should
- Have support for Cursor CLI, Claude CLI and Gemini CLI
- Support Firecracker on Unix systems

## Quick Start

### 1. Install Prerequisites

You'll need:
- **Docker** — The container runtime ([Get Docker](https://docs.docker.com/get-docker/))
- **Dev Containers CLI** — Microsoft's standard container tooling ([Install guide](https://github.com/devcontainers/cli#installation))

### 2. Install jail

Git-based install (recommended for early testers):

```bash
# Using pipx (recommended - installs in isolated environment)
pipx install 'git+https://github.com/<org>/<repo>@v0.0.1'

# Using uv tool
uv tool install 'git+https://github.com/<org>/<repo>@v0.0.1'

# Using pip (in a virtual environment)
pip install 'git+https://github.com/<org>/<repo>@v0.0.1'
```

For development or to track the latest changes:

```bash
git clone https://github.com/<org>/<repo>
cd jail
uv sync  # then: uv run jail --help
```
### 3. Create Your First Jail

```bash
cd your-project
jail init "a Node.js web server with Express"
```

This creates a `.devcontainer/` folder with everything configured. The container includes Node.js, Python, and Codex pre-installed.

The description is important, because an AI workflow will adapt your container setup to the project you describe. So help it anticipate
your requirements. E.g.

- "A data analytics pipeline in python"
- "A Next.js app with Sanity for content management"
- "A terminal based port of Final Fantasy III using Node+Ink"
- "A visualization of magnetic fields in C/sdl2"

### 4. Use It

**Interactive development:**
```bash
jail  # Opens a shell inside the container
```

**Run AI agent(s) safely:**
```bash
jail codex
```

Your `~/.codex` configuration is automatically available (read-only) inside the container, so your API keys work without exposing them to modifications.

## Development

Want to contribute? Awesome! Here's how to get started:

```bash
# Setup
uv sync  # or: pip install -e .[dev]

# Run tests
uv run pytest -q
uv run pytest -q -m integration  # Requires Docker

# Code quality
uv run ruff check .
uv run black .
uv run mypy src
```
