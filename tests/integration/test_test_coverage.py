from pipeline.llm.client import MockLLMClient
from pipeline.scenario_generator import ScenarioGenerator


def test_generated_tests_cover_all_requirements() -> None:
    llm_response = """
    {
      "test_cases": [
        {
          "id": "TC-AUTH-001-001",
          "requirement_id": "AUTH-001",
          "title": "Successful authentication",
          "description": "Verify valid login.",
          "priority": "high",
          "type": "positive",
          "preconditions": [],
          "steps": [
            "Enter valid credentials"
          ],
          "expected_result": "User is authenticated."
        },
        {
          "id": "TC-AUTH-002-001",
          "requirement_id": "AUTH-002",
          "title": "Invalid password",
          "description": "Verify invalid password handling.",
          "priority": "high",
          "type": "negative",
          "preconditions": [],
          "steps": [
            "Enter invalid password"
          ],
          "expected_result": "Authentication fails."
        }
      ]
    }
    """

    generator = ScenarioGenerator(MockLLMClient(llm_response))

    checklist = {"project": {"name": "AI-driven QA Demo"},
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

    contract = generator.generate(checklist)

    generated_requirements = {case["requirement_id"]for case in contract["test_cases"]}

    expected_requirements = {requirement["id"]for requirement in checklist["requirements"]}

    assert generated_requirements == expected_requirements