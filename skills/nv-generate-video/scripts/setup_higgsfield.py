#!/usr/bin/env python3
"""One-time Higgsfield setup helper for nv-generate-video."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = SKILL_ROOT.parents[1]
SHARED_ROOT = REPO_ROOT / "shared"
sys.path.insert(0, str(SHARED_ROOT))

from higgsfield_cli import setup_higgsfield  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Install/login/select workspace for Higgsfield CLI")
    parser.add_argument(
        "--no_login",
        action="store_true",
        help="Only check current auth state; do not start browser login.",
    )
    args = parser.parse_args()

    print("Setting up Higgsfield for nv-generate-video...")
    print("- installing local CLI if missing")
    print("- checking auth token")
    if not args.no_login:
        print("- starting browser login if needed")
    print("- selecting the only available workspace automatically")

    result = setup_higgsfield(login=not args.no_login)
    print(json.dumps({"ok": True, **result}, ensure_ascii=False, indent=2))
    print("Higgsfield setup complete.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # noqa: BLE001
        print(str(exc), file=sys.stderr)
        raise SystemExit(1) from exc
