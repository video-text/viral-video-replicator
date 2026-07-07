"""Local model capabilities."""

from __future__ import annotations

from dataclasses import dataclass

from config import load_model_config


@dataclass(frozen=True)
class VideoModel:
    id: str
    label: str
    provider: str
    default_orientation: str
    default_seconds: int
    default_definition: str
    orientations: tuple[str, ...]
    definitions: tuple[str, ...]
    duration_enum: tuple[int, ...] | None
    duration_min: int | None
    duration_max: int | None
    max_reference_images: int
    cli_reference_flag: str | None = None
    cli_definition_flag: str | None = "resolution"
    cli_extra_args: dict[str, str | int | float | bool] | None = None


DEFAULT_VIDEO_MODELS: tuple[VideoModel, ...] = (
    VideoModel(
        id="doubao-seedance-1-0-pro-fast",
        label="Doubao Seedance Fast",
        provider="apimart",
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
        provider="apimart",
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
        provider="apimart",
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
        provider="apimart",
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


def _tuple_or_none(value: object) -> tuple[int, ...] | None:
    if value is None:
        return None
    if isinstance(value, list):
        return tuple(int(item) for item in value)
    return None


def _tuple_str(value: object, fallback: tuple[str, ...]) -> tuple[str, ...]:
    if isinstance(value, list):
        return tuple(str(item) for item in value)
    return fallback


def _model_from_dict(item: dict) -> VideoModel:
    return VideoModel(
        id=str(item["id"]),
        label=str(item.get("label") or item["id"]),
        provider=str(item.get("provider") or "apimart"),
        default_orientation=str(item.get("default_orientation") or "9:16"),
        default_seconds=int(item.get("default_seconds") or 5),
        default_definition=str(item.get("default_definition") or "720p"),
        orientations=_tuple_str(item.get("orientations"), ("9:16",)),
        definitions=_tuple_str(item.get("definitions"), ("720p",)),
        duration_enum=_tuple_or_none(item.get("duration_enum")),
        duration_min=int(item["duration_min"]) if item.get("duration_min") is not None else None,
        duration_max=int(item["duration_max"]) if item.get("duration_max") is not None else None,
        max_reference_images=int(item.get("max_reference_images") or 0),
        cli_reference_flag=item.get("cli_reference_flag"),
        cli_definition_flag=item["cli_definition_flag"] if "cli_definition_flag" in item else "resolution",
        cli_extra_args=item.get("cli_extra_args") or None,
    )


def default_provider() -> str:
    config = load_model_config()
    return str(config.get("default_provider") or "higgsfield")


def get_video_models(provider: str | None = None) -> list[VideoModel]:
    config = load_model_config()
    configured = config.get("models")
    if isinstance(configured, list) and configured:
        models = [_model_from_dict(item) for item in configured]
    else:
        models = list(DEFAULT_VIDEO_MODELS)
    if provider:
        models = [item for item in models if item.provider == provider]
    return models


def resolve_video_request(
    *,
    provider: str | None = None,
    model: str | None = None,
    orientation: str | None = None,
    seconds: int | None = None,
    definition: str | None = None,
    reference_images: list[str] | None = None,
) -> VideoModel:
    provider_id = provider or default_provider()
    models = get_video_models(provider_id)
    if not models:
        raise ValueError(f"No video models configured for provider {provider_id}")
    model_id = model or models[0].id
    selected = next((item for item in models if item.id == model_id), None)
    if not selected:
        allowed = ", ".join(item.id for item in models)
        raise ValueError(f"Unsupported {provider_id} model {model_id}. Allowed: {allowed}")

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
        hint = ""
        if model_id.startswith("seedance") and final_seconds == 3:
            hint = " Use 4s with a 3s reference match plus 1s editing handle, or choose kling3_0/kling3_0_turbo for a 3s hook."
        raise ValueError(f"Model {model_id} requires duration >= {selected.duration_min}s.{hint}")
    if selected.duration_max is not None and final_seconds > selected.duration_max:
        raise ValueError(f"Model {model_id} supports max duration {selected.duration_max}s")

    refs = reference_images or []
    if len(refs) > selected.max_reference_images:
        raise ValueError(
            f"Model {model_id} supports at most {selected.max_reference_images} reference image(s)"
        )
    return selected
