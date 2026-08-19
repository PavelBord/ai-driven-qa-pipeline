from pipeline.llm.client import MockLLMClient
from pipeline.scenario_generator import ScenarioGenerator


def valid_llm_response() -> str:
    return """
{
  "test_cases": [
    {
      "id": "TC-AUTH-001-001",
      "requirement_id": "AUTH-001",
      "title": "Successful authentication",
      "description": "Verify authentication with valid credentials.",
      "priority": "high",
      "type": "positive",
      "preconditions": [
      "Registered user exists."
      ],
      "steps": [
        "Open the authentication page.",
        "Enter valid email.",
        "Enter valid password.",
        "Submit the authentication form."
      ],
      "expected_result": "User is authenticated successfully."
    }
  ]
}
""".strip()


def test_designer_generates_valid_contract() -> None:
    client = MockLLMClient(valid_llm_response())
    designer = ScenarioGenerator(client)

    checklist = {
        "project": {"name": "AI-driven QA Demo"},
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

    contract = designer.generate(checklist)

    assert len(contract["test_cases"]) == 1
    assert contract["test_cases"][0]["requirement_id"] == "AUTH-001"


def test_designer_sends_checklist_to_llm() -> None:
    client = MockLLMClient(valid_llm_response())
    designer = ScenarioGenerator(client)

    checklist = {
        "project": {"name": "AI-driven QA Demo"},
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

    designer.generate(checklist)

    assert client.last_prompt is not None
    assert "AI-driven QA Demo" in client.last_prompt


def test_designer_rejects_invalid_json() -> None:
    client = MockLLMClient("not valid json")
    designer = ScenarioGenerator(client)

    checklist = {"requirements": []}

    try:
        designer.generate(checklist)
    except ValueError as exc:
        assert "invalid JSON" in str(exc)
    else:
        raise AssertionError("Expected ValueError")


def test_designer_rejects_invalid_contract() -> None:
    response = '{"test_cases": []}'

    client = MockLLMClient(response)
    designer = ScenarioGenerator(client)

    checklist = {"requirements": []}

    try:
        designer.generate(checklist)
    except ValueError as exc:
        assert "Invalid test contract" in str(exc)
    else:
        raise AssertionError("Expected ValueError")
