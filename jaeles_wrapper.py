from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from tool_runner import ToolRunner


@dataclass
class JaelesWrapper:
    runner: ToolRunner
    config: dict

    def run(self, targets: list[str], output_dir: Path) -> dict:
        jaeles = self.config["path"]
        signatures_dir = self.config.get("signatures_dir", "")
        findings: list[str] = []

        for target in targets:
            cmd = [jaeles, "scan", "-u", target, "-q"]
            if signatures_dir:
                cmd.extend(["-s", signatures_dir])
            result = self.runner.run(cmd)
            if result.exit_code == 0 and result.stdout:
                findings.extend([line.strip() for line in result.stdout.splitlines() if line.strip()])

        payload = {"jaeles_findings": sorted(set(findings))}
        self.runner.write_json(output_dir / "jaeles.json", payload)
        return payload
