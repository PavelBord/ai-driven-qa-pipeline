from __future__ import annotations

import json
import logging
from typing import Any

from pipeline.config import PROMPTS_DIR
from pipeline.llm.client import LLMClient
from pipeline.page_context import load_pages_context

logger = logging.getLogger(__name__)

PROMPT_PATH = PROMPTS_DIR / "playwright-code-generation.txt"


class CodeGenerator:
    """Генератор кода на основе тестовых сценариев."""

    def __init__(self, llm_client: LLMClient) -> None:
        self.llm_client = llm_client

    def generate(self, data: dict[str, Any], pages: Any = None) -> str:
        """Генерирует код на основе данных и контекста страниц."""
        try:
            # Валидация входных данных
            if not isinstance(data, dict):
                raise TypeError("Data must be a dictionary")

            if "test_cases" not in data:
                raise ValueError("test_cases must be provided in data")

            test_cases = data["test_cases"]
            if not isinstance(test_cases, list) or len(test_cases) == 0:
                raise ValueError("test_cases must be a non-empty list")

            # Получаем контекст страниц, если не передан
            if pages is None:
                pages = load_pages_context()
            prompt = self._build_prompt(test_cases[0], pages)
            result = self.llm_client.generate(prompt)
            if not result:
                raise RuntimeError("LLM returned empty result")

            logger.info("Code generation completed successfully")
            return result

        except Exception as e:
            logger.error(f"Code generation failed: {e}")
            raise

    @staticmethod
    def _load_prompt() -> str:
        """Загружает шаблон промпта из файла."""
        try:
            return PROMPT_PATH.read_text(encoding="utf-8")
        except FileNotFoundError:
            logger.error(f"Prompt file not found at {PROMPT_PATH}")
            raise RuntimeError(
                f"Required prompt file not found: {PROMPT_PATH}")

    def _build_prompt(self, test_case: dict[str, Any], pages: Any) -> str:
        """Формирует промпт для LLM."""
        prompt_template = self._load_prompt()

        test_case_json = json.dumps(
            test_case,
            indent=2,
            ensure_ascii=False,
        )

        # Добавим правильные импорты для page objects
        import_statements = (
            "from page_objects.login_page import LoginPage\n"
            "from page_objects.product_page import ProductPage\n"
            "from page_objects.cart_page import CartPage\n"
        )

        return prompt_template.format(
            test_case=test_case_json,
            pages=str(pages) if pages is not None else "[]",
            import_statements=import_statements,
        )
