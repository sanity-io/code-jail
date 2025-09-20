from __future__ import annotations

import subprocess
import sys
from pathlib import Path
import os


def test_cli_help_runs(tmp_path: Path) -> None:
    env = dict(**os_environ_passthrough(), PYTHONPATH=str(Path.cwd() / "src"))
    out = subprocess.check_output([sys.executable, "-m", "jail.cli", "--help"], env=env)
    assert b"Devcontainer jail CLI" in out


def os_environ_passthrough() -> dict[str, str]:
    # Avoid leaking envs that can break tests; keep PATH, HOME minimal set
    keep = {"PATH", "HOME", "SHELL", "USER"}
    return {k: v for k, v in dict(**os.environ).items() if k in keep}
