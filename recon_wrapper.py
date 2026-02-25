from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from tool_runner import ToolRunner


@dataclass
class ReconWrapper:
    runner: ToolRunner
    scanners: dict

    def run(self, targets: list[str], output_dir: Path) -> dict:
        output: dict[str, list[str]] = {
            "subdomains": [],
            "urls": [],
        }

        for domain in targets:
            subfinder = self.scanners["subfinder"]["path"]
            amass = self.scanners["amass"]["path"]
            gau = self.scanners["gau"]["path"]
            waybackurls = self.scanners["waybackurls"]["path"]

            for cmd in (
                [subfinder, "-d", domain, "-silent"],
                [amass, "enum", "-passive", "-d", domain],
                [gau, domain],
                [waybackurls, domain],
            ):
                result = self.runner.run(cmd)
                if result.exit_code == 0 and result.stdout:
                    lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]
                    if cmd[0] in (subfinder, amass):
                        output["subdomains"].extend(lines)
                    else:
                        output["urls"].extend(lines)

        output["subdomains"] = sorted(set(output["subdomains"]))
        output["urls"] = sorted(set(output["urls"]))
        self.runner.write_json(output_dir / "recon.json", output)
        return output
