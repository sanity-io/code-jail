from __future__ import annotations

import subprocess
import sys
from pathlib import Path
import os


def run_cli(tmp_path: Path, *args: str) -> subprocess.CompletedProcess[bytes]:
    env = dict(os.environ)
    env["PYTHONPATH"] = str(Path.cwd() / "src")
    return subprocess.run(
        [sys.executable, "-m", "jail.cli", *args], cwd=tmp_path, capture_output=True, env=env
    )


def test_init_existing_requires_overwrite_non_interactive(tmp_path: Path) -> None:
    # Pre-create a devcontainer directory to simulate previous init
    (tmp_path / ".devcontainer").mkdir()
    cp = run_cli(tmp_path, "init", "--non-interactive", "--no-validate")
    assert cp.returncode == 1
    assert b"already exists" in cp.stdout + cp.stderr


def test_init_overwrite_non_interactive_succeeds(tmp_path: Path) -> None:
    (tmp_path / ".devcontainer").mkdir()
    cp = run_cli(tmp_path, "init", "--non-interactive", "--overwrite", "--no-validate")
    assert cp.returncode == 0
    # Files should be present after overwrite
    assert (tmp_path / ".devcontainer" / "devcontainer.json").exists()
    assert (tmp_path / ".devcontainer" / "Dockerfile").exists()

