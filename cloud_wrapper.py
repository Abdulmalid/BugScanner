from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from tool_runner import ToolRunner


@dataclass
class CloudWrapper:
    runner: ToolRunner
    scanners: dict
    cloud_options: dict

    def run(self, targets: list[str], output_dir: Path) -> dict:
        s3scanner = self.scanners["s3scanner"]["path"]
        cloudenum = self.scanners["cloudenum"]["path"]
        keywords = self.cloud_options.get("keywords", [])

        cloud_lines: list[str] = []

        for word in sorted(set(keywords + targets)):
            ce = self.runner.run(["python3", cloudenum, "-k", word])
            if ce.exit_code == 0 and ce.stdout:
                cloud_lines.extend([line.strip() for line in ce.stdout.splitlines() if line.strip()])

            s3 = self.runner.run([s3scanner, "scan", "--bucket", word])
            if s3.exit_code == 0 and s3.stdout:
                cloud_lines.extend([line.strip() for line in s3.stdout.splitlines() if line.strip()])

        payload = {"cloud_findings": sorted(set(cloud_lines))}
        self.runner.write_json(output_dir / "cloud.json", payload)
        return payload
