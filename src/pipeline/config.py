from __future__ import annotations

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]

PROMPTS_DIR = BASE_DIR / "prompts"
INPUT_DIR = BASE_DIR / "input"
ARTIFACTS_DIR = BASE_DIR / "artifacts"
PAGES_DIR = ARTIFACTS_DIR / "pages"
GENERATED_DIR = ARTIFACTS_DIR / "generated"
SCENARIOS_DIR = ARTIFACTS_DIR / "scenarios"
REVIEW_DIR = ARTIFACTS_DIR / "code-review"
BUG_REPORT_DIR = ARTIFACTS_DIR / "bug-reports"
EXECUTION_DIR = ARTIFACTS_DIR / "execution"
PII_DIR = ARTIFACTS_DIR / "pii"
MANIFEST_PATH = ARTIFACTS_DIR / "manifest.json"

ARTIFACT_DIRS = (
    PII_DIR,
    PAGES_DIR,
    SCENARIOS_DIR,
    GENERATED_DIR,
    REVIEW_DIR,
    BUG_REPORT_DIR,
    EXECUTION_DIR,
)