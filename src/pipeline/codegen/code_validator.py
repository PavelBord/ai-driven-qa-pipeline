from __future__ import annotations

import ast


class CodeValidationError(Exception):
    pass


class CodeValidator:
    @staticmethod
    def validate(code: str) -> None:
        try:
            ast.parse(code)

        except SyntaxError as exc:raise CodeValidationError("Generated code contains syntax errors") from exc