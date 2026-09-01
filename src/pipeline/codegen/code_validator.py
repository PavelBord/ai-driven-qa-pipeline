from __future__ import annotations

import ast

FORBIDDEN_PAGE_METHODS = ("goto", "click", "fill")


class CodeValidationError(Exception):
    pass


def strip_code_fences(code: str) -> str:
    """Remove markdown fences and trailing garbage from LLM-generated code."""
    text = code.strip()

    if text.startswith("```"):
        first_newline = text.find("\n")
        if first_newline != -1:
            text = text[first_newline + 1 :]

    closing_fence = text.rfind("```")
    if closing_fence != -1:
        text = text[:closing_fence]

    return text.strip()


def _test_functions(tree: ast.Module) -> list[ast.FunctionDef | ast.AsyncFunctionDef]:
    return [
        node
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name.startswith("test_")
    ]


def _string_literals(node: ast.AST) -> list[str]:
    return [
        child.value
        for child in ast.walk(node)
        if isinstance(child, ast.Constant) and isinstance(child.value, str)
    ]


def _is_forbidden_direct_page_call(node: ast.AST) -> bool:
    if not isinstance(node, ast.Call):
        return False
    func = node.func
    if not isinstance(func, ast.Attribute):
        return False
    if not (isinstance(func.value, ast.Name) and func.value.id == "page"):
        return False
    return func.attr in FORBIDDEN_PAGE_METHODS


def _looks_like_selector(value: str) -> bool:
    lowered = value.strip().lower()
    prefixes = ("#", ".", "[", "//", "xpath=", "css=", "text=", "role=")
    if lowered.startswith(prefixes):
        return True
    return any(f" {marker}" in lowered for marker in ("xpath=", "css=", "text=", "role="))


def validate_structure(code: str) -> list[str]:
    """Deterministic structural checks against LLM-generated test code.

    Mirrors the rules declared in the code-generation prompt:
    exactly one test function, no direct page.click/fill/goto, no hardcoded locators.
    """
    try:
        tree = ast.parse(code)
    except SyntaxError as exc:
        return [f"invalid Python syntax: {exc}"]

    functions = _test_functions(tree)

    if not functions:
        return ["no test function defined (expected exactly one `def test_*`)"]

    issues: list[str] = []

    if len(functions) > 1:
        names = ", ".join(fn.name for fn in functions)
        issues.append(f"expected exactly one test function, found {len(functions)}: {names}")

    for fn in functions:
        for node in ast.walk(fn):
            if _is_forbidden_direct_page_call(node):
                call_node = node
                name = call_node.func.attr  # type: ignore[attr-defined]
                issues.append(f"forbidden direct playwright call `page.{name}(...)` in {fn.name}")

        for literal in _string_literals(fn):
            if _looks_like_selector(literal):
                issues.append(f"hardcoded locator/selector in {fn.name}: {literal!r}")

    return issues


class CodeValidator:
    @staticmethod
    def validate(code: str) -> None:
        issues = validate_structure(code)
        if issues:
            raise CodeValidationError("; ".join(issues))