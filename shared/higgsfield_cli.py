"""Higgsfield CLI adapter for nv-generate-video."""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import tarfile
import tempfile
import urllib.request
from pathlib import Path
from typing import Any

from apimart_client import download_file
from capabilities import VideoModel


ENV_KEYS = {
    "HF_KEY",
    "HF_API_KEY",
    "HF_API_SECRET",
    "HIGGSFIELD_API_KEY",
    "HIGGSFIELD_API_SECRET",
}
CLI_VERSION = "1.1.8"
WINDOWS_AMD64_SHA256 = "9e04e5759b3c5588c181fe87d9b5b9a78e9a13a77175e92939f5f75fc4c392c4"


def load_local_env() -> dict[str, str]:
    env = os.environ.copy()
    codex_home = Path.home() / ".codex"
    bundled_deps = Path.home() / ".cache" / "codex-runtimes" / "codex-primary-runtime" / "dependencies"
    path_entries = [
        codex_home / "bin",
        bundled_deps / "node" / "bin",
        bundled_deps / "bin",
    ]
    existing_path = env.get("PATH", "")
    env["PATH"] = os.pathsep.join([str(item) for item in path_entries if item.exists()] + [existing_path])
    candidates = []
    for item in (Path.cwd(), *Path.cwd().parents):
        candidates.append(item / ".env")
    candidates.extend(
        [
            Path(__file__).resolve().parents[1] / ".env",
            codex_home / ".env",
        ]
    )
    for env_path in candidates:
        if not env_path.exists():
            continue
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            if key in ENV_KEYS and key not in env:
                env[key] = value.strip().strip('"').strip("'")
    if "HF_KEY" not in env and env.get("HIGGSFIELD_API_KEY") and env.get("HIGGSFIELD_API_SECRET"):
        env["HF_KEY"] = f"{env['HIGGSFIELD_API_KEY']}:{env['HIGGSFIELD_API_SECRET']}"
    return env


def ensure_higgsfield_cli() -> str:
    for name in ("higgsfield.exe", "higgsfield.cmd", "higgsfield"):
        candidate = Path.home() / ".codex" / "bin" / name
        if candidate.exists():
            return str(candidate)
    env = load_local_env()
    executable = shutil.which("higgsfield", path=env.get("PATH"))
    if not executable:
        raise RuntimeError(
            "Missing Higgsfield CLI. Install it with `npm install -g @higgsfield/cli`, "
            "or run `python scripts/setup_higgsfield.py`."
        )
    return executable


def install_higgsfield_cli() -> Path:
    bin_dir = Path.home() / ".codex" / "bin"
    bin_dir.mkdir(parents=True, exist_ok=True)
    target = bin_dir / "higgsfield.exe"
    if target.exists():
        return target

    url = (
        "https://github.com/higgsfield-ai/cli/releases/download/"
        f"v{CLI_VERSION}/hf_{CLI_VERSION}_windows_amd64.tar.gz"
    )
    with tempfile.TemporaryDirectory(prefix="higgsfield-cli-") as tmp:
        archive = Path(tmp) / "higgsfield.tar.gz"
        urllib.request.urlretrieve(url, archive)
        import hashlib

        digest = hashlib.sha256(archive.read_bytes()).hexdigest()
        if digest != WINDOWS_AMD64_SHA256:
            raise RuntimeError("Checksum mismatch while downloading Higgsfield CLI")
        with tarfile.open(archive, "r:gz") as handle:
            member = next((item for item in handle.getmembers() if Path(item.name).name == "hf.exe"), None)
            if member is None:
                raise RuntimeError("Higgsfield CLI archive did not contain hf.exe")
            handle.extract(member, tmp)
            extracted = Path(tmp) / member.name
            shutil.copy2(extracted, target)
    return target


def _flag_name(name: str) -> str:
    return "--" + name.replace("_", "-")


def _append_value(args: list[str], flag: str, value: object) -> None:
    if value is None:
        return
    args.extend([flag, str(value).lower() if isinstance(value, bool) else str(value)])


def _append_reference_args(args: list[str], selected: VideoModel, reference_images: list[str]) -> None:
    if not reference_images or not selected.cli_reference_flag:
        return

    if selected.cli_reference_flag == "image":
        for item in reference_images:
            args.extend(["--image", item])
        return

    if selected.cli_reference_flag == "start-image":
        args.extend(["--start-image", reference_images[0]])
        if len(reference_images) > 1:
            args.extend(["--end-image", reference_images[1]])
        return

    for item in reference_images:
        args.extend([_flag_name(selected.cli_reference_flag), item])


def _parse_json_output(text: str) -> Any:
    stripped = text.strip()
    if not stripped:
        return {}
    try:
        return json.loads(stripped)
    except json.JSONDecodeError:
        for line in reversed(stripped.splitlines()):
            line = line.strip()
            if not line:
                continue
            try:
                return json.loads(line)
            except json.JSONDecodeError:
                continue
    raise RuntimeError(f"Higgsfield CLI did not return JSON: {stripped[:500]}")


def _run(args: list[str], timeout_sec: int | None = None) -> subprocess.CompletedProcess[str]:
    executable = ensure_higgsfield_cli()
    env = load_local_env()
    return subprocess.run(
        [executable, *args],
        check=False,
        capture_output=True,
        text=True,
        timeout=timeout_sec,
        env=env,
    )


def _run_json(args: list[str], timeout_sec: int | None = None) -> Any:
    completed = _run(args, timeout_sec=timeout_sec)
    if completed.returncode != 0:
        message = (completed.stderr or completed.stdout).strip()
        raise RuntimeError(f"Higgsfield CLI failed: {message}")
    return _parse_json_output(completed.stdout)


def _error_text(completed: subprocess.CompletedProcess[str]) -> str:
    return (completed.stderr or completed.stdout or "").strip()


def _needs_login(message: str) -> bool:
    normalized = message.lower()
    return "not authenticated" in normalized or "auth login" in normalized


def _needs_workspace(message: str) -> bool:
    normalized = message.lower()
    return "no workspace selected" in normalized or "workspace set" in normalized


def ensure_authenticated() -> bool:
    completed = _run(["auth", "token", "--json", "--no-color"], timeout_sec=30)
    if completed.returncode == 0:
        return True
    message = _error_text(completed)
    if _needs_login(message):
        raise RuntimeError("Higgsfield is not authenticated. Run `python scripts/setup_higgsfield.py` once.")
    raise RuntimeError(f"Higgsfield auth check failed: {message}")


def _extract_workspace_items(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    if isinstance(payload, dict):
        for key in ("workspaces", "items", "data", "results"):
            value = payload.get(key)
            if isinstance(value, list):
                return [item for item in value if isinstance(item, dict)]
    return []


def _workspace_id(item: dict[str, Any]) -> str | None:
    for key in ("id", "workspace_id", "workspaceId", "uuid"):
        value = item.get(key)
        if isinstance(value, str) and value:
            return value
    return None


def _workspace_name(item: dict[str, Any]) -> str:
    for key in ("name", "display_name", "displayName", "slug"):
        value = item.get(key)
        if isinstance(value, str) and value:
            return value
    return "(unnamed workspace)"


def _first_workspace_id_from_text(text: str) -> str | None:
    match = re.search(
        r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}",
        text,
    )
    return match.group(0) if match else None


def list_workspaces() -> list[dict[str, Any]]:
    completed = _run(["workspace", "list", "--json", "--no-color"], timeout_sec=60)
    if completed.returncode != 0:
        message = _error_text(completed)
        if _needs_login(message):
            raise RuntimeError("Higgsfield is not authenticated. Run `python scripts/setup_higgsfield.py` once.")
        raise RuntimeError(f"Higgsfield workspace list failed: {message}")
    try:
        return _extract_workspace_items(_parse_json_output(completed.stdout))
    except RuntimeError:
        workspace_id = _first_workspace_id_from_text(completed.stdout)
        return [{"id": workspace_id}] if workspace_id else []


def set_workspace(workspace_id: str) -> None:
    completed = _run(["workspace", "set", workspace_id], timeout_sec=60)
    if completed.returncode != 0:
        raise RuntimeError(f"Higgsfield workspace set failed: {_error_text(completed)}")


def ensure_workspace_selected() -> str | None:
    completed = _run(["workspace", "status", "--json", "--no-color"], timeout_sec=30)
    if completed.returncode == 0:
        try:
            payload = _parse_json_output(completed.stdout)
            if isinstance(payload, dict):
                selected = _workspace_id(payload) or _workspace_id(payload.get("workspace") or {})
                if selected:
                    return selected
        except RuntimeError:
            workspace_id = _first_workspace_id_from_text(completed.stdout)
            if workspace_id:
                return workspace_id

    message = _error_text(completed)
    if completed.returncode != 0 and _needs_login(message):
        raise RuntimeError("Higgsfield is not authenticated. Run `python scripts/setup_higgsfield.py` once.")

    workspaces = list_workspaces()
    if not workspaces:
        raise RuntimeError("No Higgsfield workspaces are available for this account.")
    if len(workspaces) > 1:
        names = ", ".join(f"{_workspace_id(item)} ({_workspace_name(item)})" for item in workspaces)
        raise RuntimeError(f"Multiple Higgsfield workspaces found. Select one with `higgsfield workspace set <id>`: {names}")
    workspace_id = _workspace_id(workspaces[0])
    if not workspace_id:
        raise RuntimeError(f"Workspace response did not include an id: {workspaces[0]}")
    set_workspace(workspace_id)
    return workspace_id


def setup_higgsfield(*, login: bool = True) -> dict[str, Any]:
    executable = install_higgsfield_cli()
    auth_ok = False
    token_check = _run(["auth", "token", "--json", "--no-color"], timeout_sec=30)
    if token_check.returncode == 0:
        auth_ok = True
    elif login and _needs_login(_error_text(token_check)):
        login_result = _run(["auth", "login"], timeout_sec=300)
        if login_result.returncode != 0:
            raise RuntimeError(f"Higgsfield login failed: {_error_text(login_result)}")
        auth_ok = True
    elif _needs_login(_error_text(token_check)):
        raise RuntimeError("Higgsfield is not authenticated. Re-run with login enabled.")
    else:
        raise RuntimeError(f"Higgsfield auth check failed: {_error_text(token_check)}")

    workspace_id = ensure_workspace_selected() if auth_ok else None
    config_dir = Path.home() / ".codex" / "config"
    config_dir.mkdir(parents=True, exist_ok=True)
    setup_state = {
        "higgsfield_executable": str(executable),
        "authenticated": auth_ok,
        "workspace_id": workspace_id,
    }
    (config_dir / "higgsfield_setup.json").write_text(
        json.dumps(setup_state, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return setup_state


def _walk(value: Any):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from _walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk(child)


def extract_job_id(payload: Any) -> str | None:
    if isinstance(payload, str):
        return payload
    for item in _walk(payload):
        for key in ("job_id", "id", "request_id"):
            value = item.get(key)
            if isinstance(value, str) and value:
                return value
    return None


def extract_video_url(payload: Any) -> str | None:
    preferred = ("result_url", "video_url", "download_url", "url")
    for item in _walk(payload):
        for key in preferred:
            value = item.get(key)
            if isinstance(value, str) and value.startswith(("http://", "https://")):
                return value
        for key in ("videos", "video", "result", "outputs"):
            value = item.get(key)
            if isinstance(value, str) and value.startswith(("http://", "https://")):
                return value
    return None


def build_create_args(
    *,
    selected: VideoModel,
    prompt: str,
    orientation: str,
    seconds: int,
    definition: str,
    reference_images: list[str],
    wait: bool,
    poll_interval: int,
    timeout_sec: int,
) -> list[str]:
    args = [
        "generate",
        "create",
        selected.id,
        "--prompt",
        prompt,
        "--aspect-ratio",
        orientation,
        "--duration",
        str(seconds),
    ]
    if selected.cli_definition_flag:
        args.extend([_flag_name(selected.cli_definition_flag), definition])
    for key, value in (selected.cli_extra_args or {}).items():
        _append_value(args, _flag_name(key), value)
    _append_reference_args(args, selected, reference_images)
    if wait:
        args.extend(["--wait", "--wait-timeout", f"{timeout_sec}s", "--wait-interval", f"{poll_interval}s"])
    args.extend(["--json", "--no-color"])
    return args


def submit_higgsfield_video(
    *,
    selected: VideoModel,
    prompt: str,
    orientation: str,
    seconds: int,
    definition: str,
    reference_images: list[str],
    poll_interval: int,
    timeout_sec: int,
) -> tuple[str | None, str | None, Any]:
    ensure_authenticated()
    ensure_workspace_selected()
    args = build_create_args(
        selected=selected,
        prompt=prompt,
        orientation=orientation,
        seconds=seconds,
        definition=definition,
        reference_images=reference_images,
        wait=True,
        poll_interval=poll_interval,
        timeout_sec=timeout_sec,
    )
    completed = _run(args, timeout_sec=timeout_sec + 60)
    if completed.returncode != 0 and _needs_workspace(_error_text(completed)):
        ensure_workspace_selected()
        completed = _run(args, timeout_sec=timeout_sec + 60)
    if completed.returncode != 0:
        raise RuntimeError(f"Higgsfield CLI failed: {_error_text(completed)}")
    payload = _parse_json_output(completed.stdout)
    return extract_job_id(payload), extract_video_url(payload), payload


def get_higgsfield_video_status(
    *,
    job_id: str,
    wait: bool,
    poll_interval: int,
    timeout_sec: int,
) -> tuple[str | None, Any]:
    command = "wait" if wait else "get"
    args = ["generate", command, job_id, "--json", "--no-color"]
    if wait:
        args.extend(["--wait-timeout", f"{timeout_sec}s", "--wait-interval", f"{poll_interval}s"])
    ensure_authenticated()
    ensure_workspace_selected()
    payload = _run_json(args, timeout_sec=timeout_sec + 60 if wait else 120)
    return extract_video_url(payload), payload


__all__ = [
    "download_file",
    "extract_job_id",
    "extract_video_url",
    "get_higgsfield_video_status",
    "install_higgsfield_cli",
    "ensure_authenticated",
    "ensure_workspace_selected",
    "list_workspaces",
    "set_workspace",
    "setup_higgsfield",
    "submit_higgsfield_video",
]
