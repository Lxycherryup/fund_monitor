from __future__ import annotations

import json
from pathlib import Path


class JsonStateStore:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self._state = self._load()

    def has_sent(self, day: str, kind: str, code: str) -> bool:
        return self._key(day, kind, code) in self._state["sent"]

    def mark_sent(self, day: str, kind: str, code: str) -> None:
        self._state["sent"][self._key(day, kind, code)] = True
        self._save()

    def _load(self) -> dict:
        if not self.path.exists():
            return {"sent": {}}
        with self.path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        if not isinstance(data, dict):
            return {"sent": {}}
        sent = data.get("sent")
        if not isinstance(sent, dict):
            sent = {}
        return {"sent": sent}

    def _save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("w", encoding="utf-8") as handle:
            json.dump(self._state, handle, ensure_ascii=False, indent=2, sort_keys=True)

    @staticmethod
    def _key(day: str, kind: str, code: str) -> str:
        return f"{day}:{kind}:{code}"
