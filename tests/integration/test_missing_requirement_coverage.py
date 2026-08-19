import pytest

from pipeline.contract_validator import ContractValidationError
from pipeline.llm.client import MockLLMClient
from pipeline.scenario_generator import ScenarioGenerator


def test_pipeline_rejects_missing_requirement_coverage() -> None:
    llm_response = """
    {
      "test_cases": [
        {
          "id": "TC-AUTH-001-001",
          "requirement_id": "AUTH-001",
          "title": "Successful authentication",
          "description": "Verify login.",
          "priority": "high",
          "type": "positive",
          "preconditions": [],
          "steps": [
            "Login"
          ],
          "expected_result": "Success"
        }
      ]
    }
    """

    generator = ScenarioGenerator(MockLLMClient(llm_response))

    checklist = { "project": {"name": "AI-driven QA Demo"},
        "requirements": [
            {
                "id": "AUTH-001",
                "title": "Successful authentication",
                "description": "User login.",
                "priority": "high",
            },
            {
                "id": "AUTH-002",
                "title": "Invalid password",
                "description": "Wrong password.",
                "priority": "high",
            },
        ],
    }

    with pytest.raises(
        ContractValidationError):generator.generate(checklist)