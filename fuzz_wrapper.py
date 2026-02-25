from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from tool_runner import ToolRunner


@dataclass
class FuzzWrapper:
    runner: ToolRunner
    config: dict

    def run(self, targets: list[str], output_dir: Path, wordlist: str) -> dict:
        ffuf = self.config["path"]
        findings: list[str] = []

        for target in targets:
            cmd = [ffuf, "-u", f"{target.rstrip('/')}/FUZZ", "-w", wordlist, "-of", "json", "-s"]
            result = self.runner.run(cmd)
            if result.exit_code == 0 and result.stdout.strip():
                findings.append(result.stdout.strip())

        payload = {"ffuf_findings": findings}
        self.runner.write_json(output_dir / "fuzz.json", payload)
        return payload
