from __future__ import annotations

import json
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from pipeline.llm.client import LLMClient


class CodeReviewResult(BaseModel):
    """
    AI code review result.
    """

    model_config = ConfigDict(extra="forbid")

    approved: bool
    score: int = Field(ge=0, le=10)
    issues: list[str]
    recommendation: str = Field(min_length=1)


class CodeReviewError(ValueError):
    """
    Raised when AI code review response is invalid.
    """


CODE_REVIEW_PROMPT = """
Ты — Senior QA Automation Engineer.

Проведи code review автотеста.

Проверь:

1. Читаемость кода.
2. Наличие корректных assertions.
3. Использование pytest best practices.
4. Отсутствие hardcoded проблемных данных.
5. Возможные ошибки тестовой логики.

Используй только переданный код.

Верни только валидный JSON.

Формат:

{{
  "approved": true,
  "score": 10,
  "issues": [],
  "recommendation": "Code looks good"
}}

Код теста:

{code}
""".strip()


class CodeReviewer:
    """
    AI-based automated code reviewer.
    """

    def __init__(self,llm_client: LLMClient) -> None:
        self.llm_client = llm_client

    def review(self,source_code: str) -> CodeReviewResult:

        prompt = CODE_REVIEW_PROMPT.format(code=source_code)

        response = self.llm_client.generate(prompt)

        return self._parse_response(response)

    @staticmethod
    def _parse_response(response: str) -> CodeReviewResult:

        try:
            data: dict[str, Any] = json.loads(response)

        except json.JSONDecodeError as exc:
            raise CodeReviewError("AI returned invalid JSON") from exc

        try:
            return CodeReviewResult.model_validate(data)

        except Exception as exc:
            raise CodeReviewError("AI response does not match contract") from exc