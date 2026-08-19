import pytest

from pipeline.contract_validator import ContractValidationError
from pipeline.llm.client import MockLLMClient
from pipeline.scenario_generator import ScenarioGenerator


def test_pipeline_rejects_extra_fields_from_llm() -> None:
    llm_response = """
    {
      "test_cases": [
        {
          "id": "TC-AUTH-001-001",
          "requirement_id": "AUTH-001",
          "title": "Successful authentication",
          "description": "Verify authentication.",
          "priority": "high",
          "type": "positive",
          "preconditions": [],
          "steps": [
            "Login user"
          ],
          "expected_result": "User authenticated.",
          "unknown_field": "should be rejected"
        }
      ]
    }
    """

    generator = ScenarioGenerator(MockLLMClient(llm_response))

    checklist = {"requirements":[
            {
                "id": "AUTH-001",
                "title": "Successful authentication",
                "description": (
                    "Registered user can authenticate."
                ),
                "priority": "high",
            }
        ]
    }

    with pytest.raises(ContractValidationError ):generator.generate(checklist)