from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from tool_runner import ToolRunner


@dataclass
class NucleiWrapper:
    runner: ToolRunner
    config: dict

    def run(self, targets: list[str], output_dir: Path) -> dict:
        nuclei = self.config["path"]
        templates_dir = self.config.get("templates_dir", "")
        severity = self.config.get("severity", "critical,high,medium")
        findings: list[str] = []

        for target in targets:
            cmd = [nuclei, "-u", target, "-severity", severity, "-silent"]
            if templates_dir:
                cmd.extend(["-t", templates_dir])
            result = self.runner.run(cmd)
            if result.exit_code == 0 and result.stdout:
                findings.extend([line.strip() for line in result.stdout.splitlines() if line.strip()])

        payload = {"nuclei_findings": sorted(set(findings))}
        self.runner.write_json(output_dir / "nuclei.json", payload)
        return payload
