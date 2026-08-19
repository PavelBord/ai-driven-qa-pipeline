from pathlib import Path

from pipeline.checklist_loader import load_checklist
from pipeline.llm.client import MockLLMClient
from pipeline.pii_guard import PIIGuard
from pipeline.scenario_generator import ScenarioGenerator


def test_full_pipeline_with_pii_protection() -> None:
    checklist = load_checklist(Path("input/business-checklist.yaml"))

    raw_data = checklist.model_dump()

    masked_data, report = PIIGuard().scan_and_mask(raw_data)

    assert report.pii_detected is True
    assert report.total_matches == 5

    assert (masked_data["requirements"][0]["test_data"]["email"]== "<EMAIL>")

    assert (masked_data["requirements"][0]["test_data"]["password"]== "<PASSWORD>")

    llm_response = """
{
  "test_cases": [
    {
      "id": "TC-AUTH-001-001",
      "requirement_id": "AUTH-001",
      "title": "Successful authentication",
      "description": "Verify authentication scenario.",
      "priority": "high",
      "type": "positive",
      "preconditions": [],
      "steps": [
        "Authenticate user"
      ],
      "expected_result": "User is authenticated."
    },
    {
      "id": "TC-AUTH-002-001",
      "requirement_id": "AUTH-002",
      "title": "Invalid password",
      "description": "Verify authentication failure.",
      "priority": "high",
      "type": "negative",
      "preconditions": [],
      "steps": [
        "Enter invalid password"
      ],
      "expected_result": "Authentication fails."
    },
    {
      "id": "TC-AUTH-003-001",
      "requirement_id": "AUTH-003",
      "title": "Empty email",
      "description": "Verify empty email validation.",
      "priority": "medium",
      "type": "validation",
      "preconditions": [],
      "steps": [
        "Submit empty email"
      ],
      "expected_result": "Authentication fails."
    },
    {
      "id": "TC-AUTH-004-001",
      "requirement_id": "AUTH-004",
      "title": "Empty password",
      "description": "Verify empty password validation.",
      "priority": "medium",
      "type": "validation",
      "preconditions": [],
      "steps": [
        "Submit empty password"
      ],
      "expected_result": "Authentication fails."
    },
    {
      "id": "TC-AUTH-005-001",
      "requirement_id": "AUTH-005",
      "title": "Invalid email format",
      "description": "Verify invalid email format validation.",
      "priority": "medium",
      "type": "validation",
      "preconditions": [],
      "steps": [
        "Enter invalid email format"
      ],
      "expected_result": "Authentication fails."
    }
  ]
}
"""

    mock_client = MockLLMClient(llm_response)

    generator = ScenarioGenerator(mock_client)

    contract = generator.generate(masked_data)

    assert len(contract["test_cases"]) == 5

    generated_ids = {test_case["requirement_id"]
    for test_case in contract["test_cases"]}
    assert generated_ids == {
    "AUTH-001",
    "AUTH-002",
    "AUTH-003",
    "AUTH-004",
    "AUTH-005",
    }
    assert mock_client.last_prompt is not None

    assert "<EMAIL>" in mock_client.last_prompt
    assert "<PASSWORD>" in mock_client.last_prompt

    assert "user@example.com" not in mock_client.last_prompt
    assert "DemoPassword123" not in mock_client.last_prompt