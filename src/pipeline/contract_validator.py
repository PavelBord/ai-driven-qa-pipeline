from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import validate
from jsonschema.exceptions import ValidationError


class ContractValidationError(Exception):
    pass


def validate_test_contract(contract: dict[str, Any]) -> None:

    schema_path = Path(__file__).resolve().parents[2] / "schemas" / "test-contract.schema.json"

    try:
        schema_data = json.loads(schema_path.read_text(encoding="utf-8"))

    except FileNotFoundError as exc:
        raise ContractValidationError(f"Schema file not found: {schema_path}") from exc

    try:
        validate(instance=contract, schema=schema_data)

    except ValidationError as exc:
        raise ContractValidationError(str(exc)) from exc