from pathlib import Path

from pipeline.checklist_loader import load_checklist
from pipeline.ollama_client import OllamaClient
from pipeline.scenario_generator import ScenarioGenerator


def test_petstore_contract_generation() -> None:

    checklist = load_checklist(Path("input/petstore-checklist.yaml"))

    client = OllamaClient(model="qwen3.5:9b")

    generator = ScenarioGenerator(client)

    result = generator.generate(checklist.model_dump())

    assert "test_cases" in result

    assert len(result["test_cases"]) > 0