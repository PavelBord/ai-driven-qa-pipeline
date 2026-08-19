from pathlib import Path

import yaml

from pipeline.models import BusinessChecklist


def load_checklist(path: Path) -> BusinessChecklist:
    with path.open("r", encoding="utf-8") as file:
        data = yaml.safe_load(file)

    return BusinessChecklist.model_validate(data)