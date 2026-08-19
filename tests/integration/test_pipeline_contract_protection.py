import pytest

from pipeline.contract_validator import ContractValidationError
from pipeline.llm.client import MockLLMClient
from pipeline.scenario_generator import ScenarioGenerator


def test_pipeline_rejects_invalid_requirement_id() -> None:
    llm_response = """
    {
      "test_cases": [
        {
          "id": "TC-FAKE-001",
          "requirement_id": "FAKE-999",
          "title": "Fake test",
          "description": "Generated invalid test case.",
          "priority": "high",
          "type": "positive",
          "preconditions": [],
          "steps": [
            "Execute action"
          ],
          "expected_result": "System works."
        }
      ]
    }
    """

    mock_client = MockLLMClient(llm_response)

    generator = ScenarioGenerator(mock_client)

    checklist = {"project": { "name": "AI-driven QA Demo"},
        "requirements": [
            {
                "id": "AUTH-001",
                "title": "Successful authentication",
                "description": (
                    "Registered user can authenticate "
                    "using valid credentials."
                ),
                "priority": "high",
            }
        ],
    }

    with pytest.raises(ContractValidationError,match="Invalid requirement_id"):generator.generate(checklist)