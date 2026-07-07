"""Bundle analyze output for recreation."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
SHARED_ROOT = REPO_ROOT / "shared"
ANALYZE_LIB = REPO_ROOT / "skills" / "nv-analyze-video" / "lib"
sys.path.insert(0, str(SHARED_ROOT))
sys.path.insert(0, str(ANALYZE_LIB))

from analyze_video import run_analyze_video  # noqa: E402
from artifacts import artifacts_for_run  # noqa: E402


def run_recreate_video(
    *,
    video_path: Path,
    run_id: str,
    skill_dir: Path,
    transcript_path: Path | None = None,
    source_url: str | None = None,
    product_name: str | None = None,
    product_image: Path | None = None,
    person_image: Path | None = None,
    angle: str | None = None,
    brand: str | None = None,
    style: str | None = None,
) -> dict:
    artifacts = artifacts_for_run(skill_dir, run_id)
    artifacts.ensure()

    analyze_skill_dir = REPO_ROOT / "skills" / "nv-analyze-video"
    analyze_run_id = f"{run_id}--analyze"
    analyze_result = run_analyze_video(
        video_path=video_path,
        run_id=analyze_run_id,
        skill_dir=analyze_skill_dir,
        transcript_path=transcript_path,
        source_url=source_url,
    )

    recreate_source = {
        "reference": {
            "source_url": source_url,
            "local_video_path": str(video_path.resolve()),
        },
        "product": {
            "name": product_name,
            "product_image": str(product_image.resolve()) if product_image else None,
            "person_image": str(person_image.resolve()) if person_image else None,
        },
        "constraints": {"angle": angle, "brand": brand, "style": style},
        "analyze_run_id": analyze_result["run_id"],
        "analyze_artifacts_dir": analyze_result["artifacts_dir"],
        "analyze_result": analyze_result["result"],
    }
    artifacts.write_json("outputs/recreate_source.json", recreate_source)
    return {
        "run_id": run_id,
        "artifacts_dir": str(artifacts.root),
        "recreate_source": recreate_source,
    }
