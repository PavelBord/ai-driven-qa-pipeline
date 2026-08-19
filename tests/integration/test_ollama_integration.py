import pytest

from pipeline.ollama_client import OllamaClient


@pytest.mark.integration
def test_ollama_generates_response() -> None:
    client = OllamaClient(model="qwen3.5:9b")

    result = client.generate("Ответь только одним словом: OK")

    assert isinstance(result, str)
    assert result.strip()