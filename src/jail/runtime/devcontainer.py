from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path
from typing import Optional, Sequence

from rich.console import Console

console = Console()


def find_devcontainer_cli() -> Optional[str]:
    return shutil.which("devcontainer")


def read_configuration(workspace: Path) -> dict | None:
    cli = find_devcontainer_cli()
    if not cli:
        return None
    try:
        out = subprocess.check_output(
            [cli, "read-configuration", "--workspace-folder", str(workspace)],
            stderr=subprocess.STDOUT,
        )
        try:
            return json.loads(out.decode("utf-8"))
        except Exception:
            console.print(
                "[yellow]Could not parse read-configuration output as JSON; continuing to build.[/]"
            )
            return None
    except Exception:  # pragma: no cover - requires CLI
        console.print(
            "[yellow]read-configuration not available or failed; continuing to build.[/]"
        )
        return None


def build(workspace: Path, *, verbose: bool = False) -> bool:
    cli = find_devcontainer_cli()
    if not cli:
        console.print("[yellow]Dev Containers CLI not found. Skipping build validation.[/]")
        return False
    cmd = [cli, "build", "--workspace-folder", str(workspace)]
    console.print("Running: " + " ".join(cmd))
    try:
        subprocess.check_call(cmd)
        return True
    except subprocess.CalledProcessError:  # pragma: no cover - requires CLI
        return False


def up(workspace: Path, *, recreate: bool = True) -> bool:
    cli = find_devcontainer_cli()
    if not cli:
        console.print("[red]Dev Containers CLI not found.[/]")
        return False
    cmd = [cli, "up", "--workspace-folder", str(workspace)]
    if recreate:
        cmd.append("--remove-existing-container")
    console.print("Running: " + " ".join(cmd))
    try:
        subprocess.check_call(cmd)
        return True
    except subprocess.CalledProcessError:  # pragma: no cover - requires CLI
        return False


def exec(workspace: Path, command: Sequence[str]) -> int:
    cli = find_devcontainer_cli()
    if not cli:
        console.print("[red]Dev Containers CLI not found.[/]")
        return 127
    cmd = [cli, "exec", "--workspace-folder", str(workspace), "--", *command]
    console.print("Running: " + " ".join(cmd))
    try:
        return subprocess.call(cmd)
    except KeyboardInterrupt:  # pragma: no cover - interactive
        return 130


def exec_quiet(workspace: Path, command: Sequence[str]) -> int:
    cli = find_devcontainer_cli()
    if not cli:
        return 127
    cmd = [cli, "exec", "--workspace-folder", str(workspace), "--", *command]
    try:
        return subprocess.call(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except KeyboardInterrupt:  # pragma: no cover - interactive
        return 130
