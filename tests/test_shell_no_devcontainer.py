from __future__ import annotations

import subprocess
import sys
from pathlib import Path
import os


def test_shell_without_devcontainer_exits_with_error(tmp_path: Path) -> None:
    env = dict(os.environ)
    env["PYTHONPATH"] = str(Path.cwd() / "src")
    cp = subprocess.run(
        [sys.executable, "-m", "jail.cli"], cwd=tmp_path, capture_output=True, env=env
    )
    assert cp.returncode != 0
    assert b"No devcontainer found" in cp.stdout + cp.stderr
