"""Artifact filesystem helper."""

from __future__ import annotations

import json
from pathlib import Path


class Artifacts:
    def __init__(self, root: Path) -> None:
        self.root = root

    def ensure(self) -> None:
        for name in ("input", "transcript", "vision", "outputs", "logs"):
            (self.root / name).mkdir(parents=True, exist_ok=True)

    def write_json(self, rel_path: str, obj: object) -> Path:
        file_path = self.root / rel_path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return file_path

    def write_text(self, rel_path: str, text: str) -> Path:
        file_path = self.root / rel_path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(text, encoding="utf-8")
        return file_path


def artifacts_for_run(skill_dir: Path, run_id: str) -> Artifacts:
    return Artifacts(skill_dir / ".artifacts" / run_id)
