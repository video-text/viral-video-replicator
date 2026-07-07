"""Local model capabilities."""

from __future__ import annotations

from dataclasses import dataclass

from .config import load_model_config


@dataclass(frozen=True)
class VideoModel:
    id: str
    label: str
    default_orientation: str
    default_seconds: int
    default_definition: str
    orientations: tuple[str, ...]
    definitions: tuple[str, ...]
    duration_enum: tuple[int, ...] | None
    duration_min: int | None
    duration_max: int | None
    max_reference_images: int


DEFAULT_VIDEO_MODELS: tuple[VideoModel, ...] = (
    VideoModel(
        id="doubao-seedance-1-0-pro-fast",
        label="Doubao Seedance Fast",
        default_orientation="9:16",
        default_seconds=3,
        default_definition="480p",
        orientations=("9:16", "16:9"),
        definitions=("480p", "720p"),
        duration_enum=(3, 5),
        duration_min=None,
        duration_max=None,
        max_reference_images=1,
    ),
    VideoModel(
        id="kling-v3-omni",
        label="Kling V3 Omni",
        default_orientation="9:16",
        default_seconds=15,
        default_definition="720p",
        orientations=("9:16", "16:9"),
        definitions=("720p", "1080p"),
        duration_enum=None,
        duration_min=5,
        duration_max=15,
        max_reference_images=2,
    ),
    VideoModel(
        id="kling-v3",
        label="Kling V3",
        default_orientation="9:16",
        default_seconds=5,
        default_definition="720p",
        orientations=("9:16", "16:9"),
        definitions=("720p", "1080p"),
        duration_enum=(5, 10),
        duration_min=None,
        duration_max=None,
        max_reference_images=1,
    ),
    VideoModel(
        id="happyhorse-1.0",
        label="HappyHorse 1.0",
        default_orientation="9:16",
        default_seconds=5,
        default_definition="720p",
        orientations=("9:16",),
        definitions=("720p",),
        duration_enum=(5,),
        duration_min=None,
        duration_max=None,
        max_reference_images=0,
    ),
)


def get_video_models() -> list[VideoModel]:
    return list(DEFAULT_VIDEO_MODELS)


def resolve_video_request(
    *,
    model: str | None = None,
    orientation: str | None = None,
    seconds: int | None = None,
    definition: str | None = None,
    reference_images: list[str] | None = None,
) -> VideoModel:
    models = get_video_models()
    model_id = model or models[0].id
    selected = next((item for item in models if item.id == model_id), None)
    if not selected:
        allowed = ", ".join(item.id for item in models)
        raise ValueError(f"Unsupported model {model_id}. Allowed: {allowed}")

    final_orientation = orientation or selected.default_orientation
    final_seconds = int(seconds if seconds is not None else selected.default_seconds)
    final_definition = definition or selected.default_definition

    if final_orientation not in selected.orientations:
        raise ValueError(f"Model {model_id} does not support orientation {final_orientation}")
    if final_definition not in selected.definitions:
        raise ValueError(f"Model {model_id} does not support definition {final_definition}")
    if selected.duration_enum and final_seconds not in selected.duration_enum:
        raise ValueError(f"Model {model_id} requires duration in {selected.duration_enum}")
    if selected.duration_min is not None and final_seconds < selected.duration_min:
        raise ValueError(f"Model {model_id} requires duration >= {selected.duration_min}s")
    if selected.duration_max is not None and final_seconds > selected.duration_max:
        raise ValueError(f"Model {model_id} supports max duration {selected.duration_max}s")

    refs = reference_images or []
    if len(refs) > selected.max_reference_images:
        raise ValueError(
            f"Model {model_id} supports at most {selected.max_reference_images} reference image(s)"
        )
    return selected
