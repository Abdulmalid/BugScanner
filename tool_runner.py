from __future__ import annotations

import json
import logging
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class CommandResult:
    command: list[str]
    exit_code: int
    stdout: str
    stderr: str


class ToolRunner:
    def __init__(self, logger: logging.Logger) -> None:
        self.logger = logger

    def run(self, command: list[str], *, cwd: Path | None = None) -> CommandResult:
        executable = command[0]
        if not Path(executable).exists() and shutil.which(executable) is None:
            message = f"executable not found: {executable}"
            self.logger.warning(message)
            return CommandResult(command, 127, "", message)

        self.logger.info("running: %s", " ".join(command))
        process = subprocess.run(
            command,
            capture_output=True,
            text=True,
            cwd=str(cwd) if cwd else None,
            check=False,
        )
        return CommandResult(command, process.returncode, process.stdout, process.stderr)

    @staticmethod
    def write_json(path: Path, payload: Any) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2)
