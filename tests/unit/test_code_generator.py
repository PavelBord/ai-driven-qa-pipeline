from pipeline.llm.client import MockLLMClient
from pipeline.test_generator.code_generator import CodeGenerator


def test_generates_pytest_code() -> None:

    llm_response = """
def test_successful_authentication():
    assert True
"""

    client = MockLLMClient(llm_response)

    generator = CodeGenerator(client)

    contract = {
        "id": "TC-AUTH-001-001",
        "requirement_id": "AUTH-001",
        "title": "Successful authentication",
        "type": "positive",
    }

    result = generator.generate(contract)

    assert "def test_" in result
    assert "assert True" in result