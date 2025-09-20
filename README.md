# jail 🔒 — Safe-ish sandboxes for AI coding agents

**Give your AI coding agents a playground where they (probably) can't break anything (important).**

> 🌊 **Pure Vibes**: This just a toy project at this moment.


I am just tired of hitting "keep going" and "yes keep going" and "ok, run that command". This is not what "human in the loop" was supposed to mean.

So I run my coding agents in --dangerously-move-fast-and-break-tings mode. But that isn't advisible.

There are Docker containers and all that stuff, but I vibe up three experiments a day. No one has time to manage that stuff.

So here is `jail`. You just create a new folder, run `jail init` and answer one question about your intentions. A dev container is magicked up for you.

Then you can do `jail codex` to get an interactive session with codex from inside the jail. It can do whatever it wants there, because it is very unlikely to damage anything important from inside there.

If you need shell, you just `jail`. That's it.

---

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
pipx install 'git+https://github.com/simen/code-jail.git@main'

# Using uv tool
uv tool install 'git+https://github.com/simen/code-jail.git@main'

# Using pip (in a virtual environment)
pip install 'git+https://github.com/simen/code-jail.git@main'
```

Pin to a specific commit for reproducibility (optional):

```bash
pipx install 'git+https://github.com/simen/code-jail.git@8d81e9a'
```

For local development or to track the latest changes:

```bash
git clone https://github.com/simen/code-jail
cd code-jail
uv sync  # then: uv run jail --help
```
### 3. Create Your First Jail

```bash
cd your-project
jail init "a Node.js web server with Express"
```

This creates a `.devcontainer/` folder with everything configured. The container includes Node.js, Python, and Codex pre-installed.

The description is helpful, because an AI workflow will adapt your container setup to the project you describe. So help it anticipate
your requirements. E.g.

- "A data analytics pipeline in python"
- "A Next.js app with Sanity for content management"
- "A terminal based port of Final Fantasy III using Node+Ink"
- "A visualization of magnetic fields in C/sdl2"

If you omit it, you'll probably be fine too. Jail goes up in a heartbeat, and then you can figure it out from inside jail.

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
