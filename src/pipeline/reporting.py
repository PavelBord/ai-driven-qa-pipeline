from __future__ import annotations

import hashlib
import json
import platform
import shutil
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from pipeline.config import ARTIFACT_DIRS, MANIFEST_PATH, PROMPTS_DIR


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:12]


def _git_revision() -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            check=False,
            cwd=Path(__file__).resolve().parents[2],
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except OSError:
        pass
    return ""


def collect_manifest(llm_client: Any) -> dict[str, Any]:
    prompt_hashes: dict[str, str] = {}
    if PROMPTS_DIR.exists():
        for prompt_file in sorted(PROMPTS_DIR.iterdir()):
            if prompt_file.is_file():
                prompt_hashes[prompt_file.name] = _sha256(prompt_file)

    model = getattr(llm_client, "model", None)
    if model is None:
        model = type(llm_client).__name__

    return {
        "timestamp": datetime.now(UTC).isoformat(),
        "git_revision": _git_revision(),
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "llm": str(model),
        "ci": "CI" in __import__("os").environ,
        "prompt_hashes": prompt_hashes,
    }


def write_manifest(llm_client: Any) -> Path:
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    manifest = collect_manifest(llm_client)
    MANIFEST_PATH.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return MANIFEST_PATH


def clear_artifacts() -> None:
    """Remove all regenerable artifact directories for a clean, reproducible run."""
    import os

    if os.environ.get("QA_CLEAN_ARTIFACTS", "1") == "0":
        return

    for directory in ARTIFACT_DIRS:
        shutil.rmtree(directory, ignore_errors=True)