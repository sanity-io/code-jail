from __future__ import annotations

import subprocess
import sys
from pathlib import Path
import os


def test_codex_help(tmp_path: Path) -> None:
    env = dict(os.environ)
    env["PYTHONPATH"] = str(Path.cwd() / "src")
    out = subprocess.check_output(
        [sys.executable, "-m", "jail.cli", "codex", "--help"], cwd=tmp_path, env=env
    )
    assert b"Run codex inside the devcontainer" in out

