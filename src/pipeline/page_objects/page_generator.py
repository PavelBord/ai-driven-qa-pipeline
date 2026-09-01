from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from pipeline.codegen.code_validator import strip_code_fences
from pipeline.config import PAGES_DIR, PROMPTS_DIR
from pipeline.formatting import format_python
from pipeline.llm.client import LLMClient

PROMPT_PATH = PROMPTS_DIR / "page-object-generation.txt"


class PageGenerator:

    def __init__(
        self,
        llm_client: LLMClient,
    ) -> None:

        self.llm_client = llm_client

    @staticmethod
    def to_module_name(page_name: str) -> str:
        """Convert a CamelCase page name to a snake_case module name."""
        return re.sub(r"(?<!^)(?=[A-Z])", "_", page_name).lower()


    def generate(
        self,
        page_data: dict[str, Any],
    ) -> str:

        prompt = self._build_prompt(
            page_data
        )

        return strip_code_fences(
            self.llm_client.generate(
                prompt
            )
        )


    @staticmethod
    def _load_prompt() -> str:

        return PROMPT_PATH.read_text(
            encoding="utf-8"
        )


    @classmethod
    def _build_prompt(
        cls,
        page_data: dict[str, Any],
    ) -> str:

        prompt = cls._load_prompt()

        return prompt.format(
            application=page_data.get(
                "application",
                "",
            ),
            page_name=page_data.get(
                "page_name",
                "",
            ),
            page_description=page_data.get(
                "description",
                "",
            ),
            elements=page_data.get(
                "elements",
                {},
            ),
        )


    @staticmethod
    def save(
        code: str,
        page_name: str,
    ) -> Path:

        PAGES_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        (PAGES_DIR / "__init__.py").touch(
            exist_ok=True,
        )

        file_path = PAGES_DIR / (
            f"{PageGenerator.to_module_name(page_name)}.py"
        )

        file_path.write_text(
            strip_code_fences(code),
            encoding="utf-8",
        )

        format_python(file_path)

        return file_path