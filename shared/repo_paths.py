"""Resolve repo root for standalone Codex installs."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS_ROOT = REPO_ROOT / "skills"
SHARED_ROOT = REPO_ROOT / "shared"
REFERENCES_ROOT = REPO_ROOT / "references"


def skill_dir(name: str) -> Path:
    return SKILLS_ROOT / name
