import httpx
import pytest

from pipeline.ollama_client import OllamaClient


def test_ollama_client_generates_response() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST"
        assert str(request.url) == ("http://localhost:11434/api/generate")

        return httpx.Response(200,json={"response": '{"test_cases": []}'})

    transport = httpx.MockTransport(handler)
    client = httpx.Client(transport=transport)

    ollama = OllamaClient(client=client)

    result = ollama.generate("Generate test cases.")

    assert result == '{"test_cases": []}'

def test_ollama_client_raises_for_http_error() -> None:
    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(500)

    client = httpx.Client(transport=httpx.MockTransport(handler))

    ollama = OllamaClient(client=client)

    try:
        ollama.generate("Generate test cases.")
    except httpx.HTTPStatusError as exc:
        assert exc.response.status_code == 500
    else:
        raise AssertionError("Expected HTTPStatusError")


def test_ollama_client_rejects_invalid_response() -> None:
    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(200,json={"response": None})

    client = httpx.Client(transport=httpx.MockTransport(handler))

    ollama = OllamaClient(client=client)

    with pytest.raises(TypeError,match="invalid response"): ollama.generate("Generate test cases.")