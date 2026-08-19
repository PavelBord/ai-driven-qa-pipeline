from __future__ import annotations

from pipeline.ollama_client import OllamaClient
from pipeline.scenario_generator import ScenarioGenerator


def test_ollama_generates_valid_test_contract() -> None:
    client = OllamaClient(model="qwen3.5:9b")

    generator = ScenarioGenerator(llm_client=client)

    checklist = {"project": {"name": "AI-driven QA Demo"},
    "requirements": [
        {
            "id": "REQ-001",
            "title": "Successful authentication",
            "description": (
                "Пользователь может войти в систему "
                "с корректными учетными данными."
            ),
            "priority": "high",
        },
        {
            "id": "REQ-002",
            "title": "Failed authentication",
            "description": (
                "При неверных учетных данных "
                "вход в систему не выполняется."
            ),
            "priority": "high",
        },
    ],
}

    result = generator.generate(checklist)

    assert isinstance(result, dict)
    assert "test_cases" in result
    assert isinstance(result["test_cases"], list)
    assert len(result["test_cases"]) > 0

    valid_requirement_ids = {"REQ-001","REQ-002"}

    for test_case in result["test_cases"]:
        assert test_case["requirement_id"] in valid_requirement_ids