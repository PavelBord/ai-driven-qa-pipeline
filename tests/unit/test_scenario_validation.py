from __future__ import annotations

import pytest

from pipeline.contract_validator import ContractValidationError, validate_test_contract
from pipeline.scenario.scenario_generation import ScenarioGenerator

CHECKLIST = {
    "requirements": [
        {"id": "USER-001", "description": "Register"},
        {"id": "USER-002", "description": "Login"},
    ]
}


def make_case(case_id: str, requirement_id: str) -> dict[str, object]:
    return {
        "id": case_id,
        "requirement_id": requirement_id,
        "title": "T",
        "description": "D",
        "type": "positive",
        "priority": "high",
        "preconditions": [],
        "steps": ["step"],
        "expected_result": "ok",
    }


def test_valid_contract_passes_schema() -> None:
    contract = {"test_cases": [make_case("TC-001", "USER-001")]}
    validate_test_contract(contract)


def test_duplicate_ids_rejected() -> None:
    contract = {
        "test_cases": [
            make_case("TC-001", "USER-001"),
            make_case("TC-001", "USER-002"),
        ]
    }

    with pytest.raises(ContractValidationError, match="Duplicate test case ids"):
        ScenarioGenerator._validate_unique_ids(contract)


def test_missing_requirement_coverage_rejected() -> None:
    contract = {"test_cases": [make_case("TC-001", "USER-001")]}

    with pytest.raises(ContractValidationError, match="Missing test coverage"):
        ScenarioGenerator._validate_requirement_coverage(contract, CHECKLIST)


def test_unknown_requirement_id_rejected() -> None:
    contract = {"test_cases": [make_case("TC-001", "NOPE-001")]}

    with pytest.raises(ContractValidationError, match="Invalid requirement_id"):
        ScenarioGenerator._validate_requirement_ids(contract, CHECKLIST)


def test_prompt_build_appends_feedback() -> None:
    prompt = ScenarioGenerator._build_prompt(CHECKLIST, feedback="Invalid id")

    assert 'USER-001' in prompt
    assert "Invalid id" in prompt