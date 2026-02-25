from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass
class ConfigManager:
    config_path: Path

    def load(self) -> dict[str, Any]:
        with self.config_path.open("r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle) or {}
        self._validate(data)
        return data

    @staticmethod
    def _validate(config: dict[str, Any]) -> None:
        if "scanners" not in config:
            raise ValueError("config missing required section: scanners")
        if "output" not in config:
            raise ValueError("config missing required section: output")

        required_scanners = [
            "nuclei",
            "jaeles",
            "subfinder",
            "httpx",
            "katana",
            "amass",
            "gau",
            "waybackurls",
            "ffuf",
            "s3scanner",
            "cloudenum",
        ]

        missing = [name for name in required_scanners if name not in config["scanners"]]
        if missing:
            raise ValueError(f"config missing scanners: {', '.join(missing)}")


__all__ = ["ConfigManager"]
