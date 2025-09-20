from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional, Tuple
import shutil
import subprocess

import typer
from rich.console import Console
from rich.panel import Panel

from . import __version__
from .scaffold import (
    preview_scaffold,
    write_scaffold,
    update_config_prompt,
)
from .runtime import devcontainer as dc

app = typer.Typer(add_completion=False, invoke_without_command=True, help="Devcontainer jail CLI")
console = Console()


@app.callback()
def _callback(  # noqa: D401
    ctx: typer.Context,
    version: Optional[bool] = typer.Option(  # noqa: FBT002
        None,
        "--version",
        callback=lambda v: (typer.echo(__version__), raise_system_exit()) if v else None,
        is_eager=True,
        help="Print version and exit",
    ),
):
    """Jail: devcontainer-focused workflow for coding agents."""
    # If invoked with no subcommand, drop into a shell
    if ctx.invoked_subcommand is None and not any(
        flag in sys.argv for flag in ("-h", "--help", "--version")
    ):
        _shell()
        raise typer.Exit()


def raise_system_exit() -> None:  # tiny helper for typer callback
    raise typer.Exit(code=0)


@app.command("init")
def cmd_init(  # noqa: D401
    prompt: Optional[str] = typer.Argument(
        None,
        help="Platform requirements prompt for adaptation (optional)",
    ),
    overwrite: bool = typer.Option(
        False, "--overwrite", help="Overwrite existing .devcontainer if present"
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Print planned actions without writing files"
    ),
    non_interactive: bool = typer.Option(
        False, "--non-interactive", help="Fail if an input would be prompted"
    ),
    no_ai_on_init: bool = typer.Option(
        False,
        "--no-ai-on-init",
        help="Skip AI adaptation during init; only scaffold the template",
    ),
    validate: bool = typer.Option(
        True, "--validate/--no-validate", help="Validate with Dev Containers CLI"
    ),
    verbose: bool = typer.Option(False, "-v", "--verbose", help="Verbose logs"),
):
    """Create a devcontainer for this repo (scaffold + optional validation)."""
    cwd = Path.cwd()
    dev_dir = cwd / ".devcontainer"

    # If already initialized, either confirm overwrite (interactive) or exit with guidance.
    if dev_dir.exists() and not overwrite:
        if non_interactive:
            console.print(
                "[yellow].devcontainer already exists. Re-run with --overwrite to re-initialize.[/]"
            )
            raise typer.Exit(1)
        if not typer.confirm(
            ".devcontainer already exists. Overwrite and re-initialize?", default=False
        ):
            console.print("[green]No changes made.[/]")
            raise typer.Exit(0)
        overwrite = True

    if prompt is None and not non_interactive:
        prompt = interactive_prompt()

    plan = preview_scaffold(cwd, overwrite=overwrite)
    console.print(Panel.fit("Devcontainer v1 focus. Docker-only runner may arrive later."))
    for action in plan:
        console.print(f"- {action}")

    if dry_run:
        raise typer.Exit(0)

    write_scaffold(cwd, overwrite=overwrite)
    if prompt:
        update_config_prompt(cwd, prompt)
    console.print("[green]Devcontainer created at .devcontainer/[/]")

    # Optional Codex adaptation (host) — keep it simple and low-friction
    if not no_ai_on_init:
        if prompt:
            _adapt_with_codex_host(cwd, prompt, verbose=verbose, non_interactive=non_interactive)
        else:
            console.print(
                "[yellow]No prompt provided; skipping Codex adaptation. Re-run with a prompt to adapt.[/]"
            )

    if validate:
        _validate_devcontainer(cwd, verbose=verbose)


def interactive_prompt() -> str:
    console.print("Describe at a high level what you plan to do.")
    console.print("E.g., ‘Python CLI with uv; needs sqlite and curl’. One or two sentences.")
    console.print("[dim](Leave blank to skip AI adaptation.)[/]")
    try:
        p = input("> ").strip()
    except (EOFError, KeyboardInterrupt):  # pragma: no cover - interactive
        p = ""
    return p


def _validate_devcontainer(cwd: Path, *, verbose: bool) -> None:
    if not dc.find_devcontainer_cli():
        console.print(
            "[yellow]Dev Containers CLI not found. Install from https://github.com/devcontainers/cli and re-run with --validate.[/]"
        )
        return
    cfg = dc.read_configuration(cwd)
    if cfg is None:
        console.print("[yellow]Skipping configuration read.[/]")
    ok = dc.build(cwd, verbose=verbose)
    if ok:
        console.print("[green]Validation succeeded (build completed).[/]")
    else:
        console.print("[red]Validation failed. Check logs above.[/]")


@app.command("shell")
def shell_cmd() -> None:
    """Open an interactive shell inside the devcontainer."""
    _shell()


def _shell() -> None:
    cwd = Path.cwd()
    if not (cwd / ".devcontainer").exists():
        console.print("[red]No devcontainer found. Run `jail init` first.[/]")
        raise typer.Exit(1)
    if not dc.up(cwd):
        raise typer.Exit(1)
    # Prefer bash; fallback to sh
    rc = dc.exec(cwd, ["bash"])
    if rc == 127:
        rc = dc.exec(cwd, ["sh"])
    raise typer.Exit(rc)


@app.command(
    "codex",
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True},
)
def codex_cmd(
    ctx: typer.Context,
    on_request: bool = typer.Option(
        False,
        "--on-request",
        help="Run codex with on-request approvals (default: dangerous)",
    ),
    workdir: Optional[str] = typer.Option(
        None,
        "--workdir",
        help="Working directory inside container (default: /workspaces/<repo>)",
    ),
    config: Optional[str] = typer.Option(
        None,
        "--config",
        help="Host codex config dir to propagate (v1 note: edit devcontainer.json mounts)",
        metavar="PATH",
    ),
    no_propagate_config: bool = typer.Option(
        False,
        "--no-propagate-config",
        help="Do not propagate host codex config (v1 note: edit devcontainer.json mounts)",
    ),
):
    """Run codex inside the devcontainer with arguments passed through."""
    cwd = Path.cwd()
    if not (cwd / ".devcontainer").exists():
        console.print("[red]No devcontainer found. Run `jail init` first.[/]")
        raise typer.Exit(1)
    if not dc.up(cwd):
        raise typer.Exit(1)

    if config or no_propagate_config:
        console.print(
            "[yellow]Note: v1 uses devcontainer.json mounts for config propagation. Update the 'mounts' entry to change or disable ~/.codex propagation.[/]"
        )

    default_workdir = f"/workspaces/{cwd.name}"
    wd = workdir or default_workdir
    # Ensure codex exists inside container
    if not dc.up(cwd):
        raise typer.Exit(1)
    rc_check = dc.exec_quiet(cwd, ["bash", "-lc", "command -v codex >/dev/null 2>&1"])
    if rc_check != 0:
        console.print(
            "[red]codex is not installed inside the container.[/] Add it to the Dockerfile or postCreateCommand, then rebuild (jail --validate)."
        )
        raise typer.Exit(2)

    # Base command
    base = ["bash", "-lc", _codex_command_line(ctx.args, on_request, wd)]
    rc = dc.exec(cwd, base)
    raise typer.Exit(rc)


def _codex_command_line(extra: list[str], on_request: bool, workdir: str) -> str:
    # Construct a shell line that refreshes ~/.codex from host mount (read-only)
    # then cd's into workdir and invokes codex
    policy_flag = "--on-request" if on_request else "--dangerously-bypass-approvals-and-sandbox"
    user_args = " ".join(_shlex_quote(a) for a in extra)
    refresh = (
        "if [ -d /home/dev/.codex-host ]; then "
        "rm -rf /home/dev/.codex && mkdir -p /home/dev/.codex && "
        "cp -a /home/dev/.codex-host/. /home/dev/.codex/; fi;"
    )
    return f"{refresh} cd {workdir} && codex {policy_flag} --skip-git-repo-check {user_args}".strip()


def _shlex_quote(s: str) -> str:
    # Minimal POSIX quoting to embed user args in a bash -lc string
    if not s:
        return "''"
    if all(c.isalnum() or c in "@%_+=:,./-" for c in s):
        return s
    return "'" + s.replace("'", "'\\''") + "'"


def _adapt_with_codex_host(cwd: Path, prompt: str, *, verbose: bool, non_interactive: bool) -> None:
    """Run host Codex in full-auto to adapt .devcontainer to the prompt.

    Defensive behavior:
    - If Codex CLI not found on host, print a note and skip.
    - If running with --non-interactive and no prompt, skip (handled by caller).
    """
    codex = shutil.which("codex")
    if not codex:
        console.print(
            "[yellow]Codex CLI not found on host; skipping adaptation. Install @openai/codex or run `jail codex` inside the container to adapt later.[/]"
        )
        return

    instruction = (
        "Adapt the Dev Container configuration for this repository based on the following high-"
        "level requirements. Modify only files under .devcontainer (Dockerfile, devcontainer.json,"
        " postCreateCommand.sh, jail.config.json). Keep a non-root user 'dev' and retain the"
        " read-only ~/.codex host mount. Ensure the final container has necessary OS packages,"
        " language/tooling versions, and codex installed. Keep changes minimal and predictable.\n\n"
        f"Requirements: {prompt}\n"
    )

    cmd = [codex, "exec", "--full-auto", "-C", str(cwd), "--skip-git-repo-check", instruction]
    if verbose:
        console.print("Running host Codex adaptation:")
        console.print(" ".join(_shlex_quote(c) for c in cmd))
    try:
        rc = subprocess.call(cmd)
        if rc == 0:
            console.print("[green]Codex adaptation completed.[/]")
        else:
            console.print(
                f"[yellow]Codex adaptation exited with code {rc}. You can re-run later or edit manually.[/]"
            )
    except Exception as e:  # pragma: no cover - defensive
        console.print(f"[yellow]Codex adaptation failed: {e}[/]")


def main() -> None:
    app()


if __name__ == "__main__":
    main()
