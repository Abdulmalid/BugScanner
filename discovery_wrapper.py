from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from tool_runner import ToolRunner


@dataclass
class DiscoveryWrapper:
    runner: ToolRunner
    scanners: dict

    def run(self, recon: dict, output_dir: Path) -> dict:
        httpx = self.scanners["httpx"]["path"]
        katana = self.scanners["katana"]["path"]

        active_hosts: list[str] = []
        crawled_urls: list[str] = []

        for host in recon.get("subdomains", []):
            result = self.runner.run([httpx, "-silent", "-u", host])
            if result.exit_code == 0 and result.stdout.strip():
                active_hosts.extend([line.strip() for line in result.stdout.splitlines() if line.strip()])

        for target in sorted(set(active_hosts)):
            result = self.runner.run([katana, "-silent", "-u", target])
            if result.exit_code == 0 and result.stdout.strip():
                crawled_urls.extend([line.strip() for line in result.stdout.splitlines() if line.strip()])

        payload = {
            "active_hosts": sorted(set(active_hosts)),
            "crawled_urls": sorted(set(crawled_urls)),
        }
        self.runner.write_json(output_dir / "discovery.json", payload)
        return payload
