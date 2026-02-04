from __future__ import annotations

import os
from pathlib import Path


def pytest_configure() -> None:
    # Ensure tests never depend on a user machine config.
    # This runs before test modules are imported.
    base = Path.cwd() / ".pytest_tmp" / "cognihub_config"
    base.mkdir(parents=True, exist_ok=True)

    os.environ["COGNIHUB_CONFIG_DIR"] = str(base)

    from cognihub import config as ch_config

    ch_config.ensure_default_config_files(base)

    # Force data dir into the test workspace.
    core_path = base / "core.toml"
    data_dir = (Path.cwd() / ".pytest_tmp" / "cognihub_data").as_posix()

    raw = core_path.read_text(encoding="utf-8")
    if "data_dir" in raw:
        lines = []
        for line in raw.splitlines(True):
            if line.strip().startswith("data_dir"):
                lines.append(f"data_dir = \"{data_dir}\"\n")
            else:
                lines.append(line)
        core_path.write_text("".join(lines), encoding="utf-8")
