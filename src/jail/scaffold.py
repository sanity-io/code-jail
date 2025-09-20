from __future__ import annotations

import os
import stat
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Iterable, List

from rich.console import Console

console = Console()


@dataclass
class PlannedAction:
    kind: str
    path: Path

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"{self.kind}: {self.path}"


def _template_root() -> Path:
    # Use filesystem path so this works in editable installs and from source.
    return Path(__file__).parent / "templates" / ".devcontainer"


def _iter_template_files(root: Path) -> Iterable[Path]:
    for p in root.rglob("*"):
        if p.is_file():
            yield p


def preview_scaffold(cwd: Path, *, overwrite: bool) -> List[PlannedAction]:
    dest_root = cwd / ".devcontainer"
    actions: List[PlannedAction] = []
    tpl_root = _template_root()
    for src in _iter_template_files(tpl_root):
        rel = src.relative_to(tpl_root)
        dest = dest_root / rel
        if dest.exists() and not overwrite:
            actions.append(PlannedAction("skip (exists)", dest))
        else:
            actions.append(PlannedAction("write", dest))
    return actions


def write_scaffold(cwd: Path, *, overwrite: bool) -> None:
    tpl_root = _template_root()
    dest_root = cwd / ".devcontainer"
    dest_root.mkdir(parents=True, exist_ok=True)

    for src in _iter_template_files(tpl_root):
        rel = src.relative_to(tpl_root)
        dest = dest_root / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.exists() and not overwrite:
            console.log(f"[yellow]skip existing[/] {dest}")
            continue
        data = src.read_bytes()
        dest.write_bytes(data)

        # Preserve executable bit for scripts
        if src.name.endswith(".sh"):
            mode = os.stat(dest).st_mode
            os.chmod(dest, mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def update_config_prompt(cwd: Path, prompt: str) -> None:
    cfg_path = cwd / ".devcontainer" / "jail.config.json"
    data = {
        "version": 1,
        "adaptedBy": "codex",
        "lastAdaptPrompt": prompt,
        "imageBase": "mcr.microsoft.com/devcontainers/base:ubuntu",
    }
    if cfg_path.exists():
        try:
            loaded = json.loads(cfg_path.read_text())
            if isinstance(loaded, dict):
                loaded.update({"lastAdaptPrompt": prompt})
                data = loaded
        except Exception:  # pragma: no cover - defensive
            pass
    cfg_path.write_text(json.dumps(data, indent=2) + "\n")


    
