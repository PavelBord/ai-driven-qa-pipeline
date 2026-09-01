from __future__ import annotations

import pytest

from pipeline.codegen.code_validator import (
    CodeValidationError,
    CodeValidator,
    strip_code_fences,
    validate_structure,
)


def test_strip_code_fences_removes_language_fence() -> None:
    assert strip_code_fences("```python\nfoo = 1\n```") == "foo = 1"


def test_strip_code_fences_removes_plain_fence() -> None:
    assert strip_code_fences("```\nfoo = 1\n```") == "foo = 1"


def test_strip_code_fences_removes_trailing_garbage() -> None:
    assert strip_code_fences("```python\nfoo = 1\n```some_filename.py") == "foo = 1"


def test_strip_code_fences_passes_through_plain_code() -> None:
    code = "def test_x(page):\n    assert True"
    assert strip_code_fences(code) == code


def test_validate_accepts_valid_code() -> None:
    CodeValidator.validate("def test_x(page):\n    assert True")


def test_validate_rejects_broken_code() -> None:
    with pytest.raises(CodeValidationError):
        CodeValidator.validate("def (<<<")


def test_validate_rejects_code_without_test_function() -> None:
    issues = validate_structure("def helper():\n    return 1\n")
    assert any("no test function" in issue for issue in issues)


def test_validate_rejects_multiple_test_functions() -> None:
    code = "def test_a(page):\n    assert True\n\ndef test_b(page):\n    assert True\n"
    issues = validate_structure(code)
    assert any("exactly one test function" in issue for issue in issues)


def test_validate_rejects_direct_page_calls() -> None:
    code = (
        "from login_page import LoginPage\n"
        "def test_login(page):\n"
        "    login_page = LoginPage(page)\n"
        "    page.click('.login-button')\n"
    )
    issues = validate_structure(code)
    assert any("page.click" in issue for issue in issues)


def test_validate_rejects_hardcoded_selectors() -> None:
    code = (
        "def test_login(page):\n"
        "    page.goto('https://example.com')\n"
        "    login_button = '.login-button'\n"
    )
    issues = validate_structure(code)
    assert any("hardcoded locator" in issue for issue in issues)


def test_validate_allows_page_object_based_code() -> None:
    code = (
        "from login_page import LoginPage\n"
        "def test_login(page):\n"
        "    login_page = LoginPage(page)\n"
        "    login_page.login('<EMAIL>', '<PASSWORD>')\n"
        "    assert login_page.is_logged_in()\n"
    )
    issues = validate_structure(code)
    assert issues == []