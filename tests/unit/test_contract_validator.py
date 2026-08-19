import pytest

from pipeline.contract_validator import ContractValidationError, validate_test_contract


def valid_contract() -> dict:
    return {"test_cases": [
            {
                "id": "TC-AUTH-001-001",
                "requirement_id": "AUTH-001",
                "title": "Successful authentication",
                "description": (
                    "Verify that a registered user can authenticate "
                    "using valid credentials."
                ),
                "priority": "high",
                "type": "positive",
                "preconditions": [
                    "Registered user exists.",
                ],
                "steps": [
                    "Open the authentication page.",
                    "Enter valid email.",
                    "Enter valid password.",
                    "Submit the authentication form.",
                ],
                "expected_result": (
                    "User is authenticated successfully."
                ),
            }
        ]
    }


def test_valid_contract_passes() -> None:
    validate_test_contract(valid_contract())


def test_missing_required_field_fails() -> None:
    contract = valid_contract()
    del contract["test_cases"][0]["expected_result"]

    with pytest.raises(ContractValidationError):
        validate_test_contract(contract)


def test_invalid_priority_fails() -> None:
    contract = valid_contract()
    contract["test_cases"][0]["priority"] = "urgent"

    with pytest.raises(ContractValidationError):
        validate_test_contract(contract)


def test_invalid_test_type_fails() -> None:
    contract = valid_contract()
    contract["test_cases"][0]["type"] = "exploratory"

    with pytest.raises(ContractValidationError):
        validate_test_contract(contract)


def test_additional_property_fails() -> None:
    contract = valid_contract()
    contract["test_cases"][0]["unknown_field"] = "not allowed"

    with pytest.raises(ContractValidationError):
        validate_test_contract(contract)


def test_empty_steps_fails() -> None:
    contract = valid_contract()
    contract["test_cases"][0]["steps"] = []

    with pytest.raises(ContractValidationError):
        validate_test_contract(contract)