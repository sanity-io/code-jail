from __future__ import annotations

from pathlib import Path

from jail.scaffold import write_scaffold


def test_write_scaffold_creates_devcontainer(tmp_path: Path) -> None:
    write_scaffold(tmp_path, overwrite=False)
    dc = tmp_path / ".devcontainer"
    assert (dc / "devcontainer.json").exists()
    assert (dc / "Dockerfile").exists()
    assert (dc / "postCreateCommand.sh").exists()
    assert (dc / "jail.config.json").exists()

