from __future__ import annotations

import json
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from pipeline.llm.client import LLMClient


class LogAnalysisResult(BaseModel):
    """
    Structured AI analysis result.
    """

    model_config = ConfigDict(extra="forbid")

    status: str = Field(min_length=1)
    error_type: str | None = None
    summary: str = Field(min_length=1)
    recommendation: str = Field(min_length=1)


ANALYSIS_PROMPT = """
Ты — Senior QA Engineer.

Проанализируй результат выполнения тестов.

Используй только предоставленные логи.

Верни только JSON.

Формат:

{{
  "status": "passed или failed",
  "error_type": "тип ошибки",
  "summary": "краткое описание проблемы",
  "recommendation": "рекомендация QA инженера"
}}

Логи выполнения:

{logs}
""".strip()

class LogAnalyzer:
    """
    AI-based test execution log analyzer.
    """

    def __init__(self,llm_client: LLMClient) -> None:
        self.llm_client = llm_client

    def analyze(self,execution_logs: str) -> LogAnalysisResult:
        prompt = ANALYSIS_PROMPT.format(logs=execution_logs)

        response = self.llm_client.generate(prompt)

        return self._parse_response(response)

    @staticmethod
    def _parse_response(response: str) -> LogAnalysisResult:

        data: dict[str, Any] = json.loads(response)

        return LogAnalysisResult.model_validate(data)