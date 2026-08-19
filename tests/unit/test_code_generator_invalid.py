import pytest

from pipeline.llm.client import MockLLMClient
from pipeline.test_generator.code_generator import CodeGenerator
from pipeline.test_generator.code_validator import CodeValidationError


def test_generator_rejects_invalid_python() -> None:

    llm_response = """
def test_login(
"""

    generator = CodeGenerator(MockLLMClient(llm_response))

    contract = {"id": "TC-AUTH-001","requirement_id": "AUTH-001"}


    with pytest.raises(CodeValidationError):
        generator.generate(contract)