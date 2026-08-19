import pytest

from pipeline.contract_validator import ContractValidationError
from pipeline.llm.client import MockLLMClient
from pipeline.scenario_generator import ScenarioGenerator


def test_pipeline_rejects_invalid_test_type() -> None:
    llm_response = """
    {
      "test_cases": [
        {
          "id": "TC-AUTH-001-001",
          "requirement_id": "AUTH-001",
          "title": "Invalid type test",
          "description": "Wrong type value.",
          "priority": "high",
          "type": "unknown",
          "preconditions": [],
          "steps": [
            "Login"
          ],
          "expected_result": "Success"
        }
      ]
    }
    """

    generator = ScenarioGenerator(
        MockLLMClient(llm_response)
    )

    checklist = {"requirements": [
            {
                "id": "AUTH-001",
                "title": "Authentication",
                "description": "User login.",
                "priority": "high",
            }
        ]
    }

    with pytest.raises(ContractValidationError):generator.generate(checklist)