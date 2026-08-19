from __future__ import annotations

import json
from typing import Any

from pipeline.llm.client import LLMClient
from pipeline.test_generator.code_validator import CodeValidator

TEST_CODE_PROMPT = """
Ты — Senior Automation QA Engineer.

Твоя задача — создать pytest автотест
на основании тестового контракта.

СТРОГИЕ ПРАВИЛА:

1. Используй только информацию из тест-контракта.

2. Не придумывай:
- API endpoints
- HTTP методы
- UI элементы
- поля
- бизнес-логику,
если этого нет в контракте.

3. Верни только Python код.

4. Код должен быть валидным pytest.

5. Не используй Markdown.

6. Создай одну тестовую функцию.

7. Имя функции должно начинаться с test_.

Тестовый контракт:

{contract}
""".strip()


class CodeGenerator:

    def __init__(self,llm_client: LLMClient) -> None:
        self.llm_client = llm_client


    def generate(self,contract: dict[str, Any]) -> str:

        prompt = self._build_prompt(contract)

        code = self.llm_client.generate(prompt)

        CodeValidator.validate(code)

        return code

    @staticmethod
    def _build_prompt(contract: dict[str, Any]) -> str:

        contract_json = json.dumps(contract,indent=2,ensure_ascii=False)

        return TEST_CODE_PROMPT.format(contract=contract_json)