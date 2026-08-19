from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

SCHEMA_PATH = (Path(__file__).resolve().parents[2]/ "schemas"/ "test-contract.schema.json")


class ContractValidationError(ValueError):
    """Raised when a generated test contract is invalid."""


def validate_test_contract(data: Any) -> None:
    """Validate a test contract against the project JSON Schema."""

    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))

    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(data),key=lambda error: list(error.path))

    if not errors:
        return

    details = "\n".join(f"{list(error.path)}: {error.message}"for error in errors)

    raise ContractValidationError(f"Invalid test contract:\n{details}")