from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Reporter:
    output_dir: Path

    def write_json(self, filename: str, payload: dict) -> Path:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        report_path = self.output_dir / filename
        with report_path.open("w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2)
        return report_path
