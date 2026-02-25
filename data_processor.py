from __future__ import annotations

from dataclasses import dataclass


@dataclass
class DataProcessor:
    @staticmethod
    def aggregate(*sections: dict) -> dict:
        merged: dict = {}
        for section in sections:
            merged.update(section)
        return merged

    @staticmethod
    def normalize(payload: dict) -> dict:
        normalized: dict = {}
        for key, value in payload.items():
            if isinstance(value, list):
                normalized[key] = sorted(set(value))
            else:
                normalized[key] = value
        return normalized
