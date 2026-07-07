"""Config helpers for standalone skill repo."""

from __future__ import annotations

import json
from pathlib import Path

from .repo_paths import REPO_ROOT

DEFAULT_MODELS_PATH = REPO_ROOT / "config" / "models.json"


def load_model_config() -> dict:
    if DEFAULT_MODELS_PATH.exists():
        return json.loads(DEFAULT_MODELS_PATH.read_text(encoding="utf-8"))
    return {}
