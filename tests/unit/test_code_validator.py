import pytest

from pipeline.test_generator.code_validator import CodeValidationError, CodeValidator


def test_valid_python_code_passes() -> None:

    code = """
def test_login():
    assert True
"""

    CodeValidator.validate(code)


def test_invalid_python_code_fails() -> None:

    code = """
def test_login(
"""

    with pytest.raises(CodeValidationError):
        CodeValidator.validate(code)