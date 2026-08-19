from pipeline.llm.client import LLMClient, MockLLMClient


def test_mock_llm_implements_llm_client() -> None:
    client = MockLLMClient('{"test_cases": []}')

    assert isinstance(client, LLMClient)


def test_mock_llm_returns_response() -> None:
    response = '{"test_cases": []}'
    client = MockLLMClient(response)

    result = client.generate("Generate test cases.")

    assert result == response


def test_mock_llm_stores_prompt() -> None:
    client = MockLLMClient('{"test_cases": []}')
    prompt = "Generate test cases."

    client.generate(prompt)

    assert client.last_prompt == prompt