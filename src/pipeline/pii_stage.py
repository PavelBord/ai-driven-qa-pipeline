from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from pipeline.pii_guard import PIIGuard


def run_pii_stage(input_path: Path,output_dir: Path) -> None:

    output_dir.mkdir(parents=True, exist_ok=True)

    with input_path.open("r", encoding="utf-8") as file:
        data: Any = yaml.safe_load(file)

    masked_data, report = PIIGuard().scan_and_mask(data)

    masked_path = output_dir / "masked-business-checklist.yaml"
    report_path = output_dir / "pii-report.json"

    with masked_path.open("w", encoding="utf-8") as file:
        yaml.safe_dump(masked_data, file,allow_unicode=True,sort_keys=False)

    report_path.write_text(report.model_dump_json(indent=2),encoding="utf-8")