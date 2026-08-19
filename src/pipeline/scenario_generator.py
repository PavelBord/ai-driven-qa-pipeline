from __future__ import annotations

import json
from typing import Any

from pipeline.contract_validator import ContractValidationError, validate_test_contract
from pipeline.llm.client import LLMClient

TEST_DESIGN_PROMPT = """
Ты — Senior QA Engineer с опытом проектирования тестов.

Твоя задача — на основании переданных бизнес-требований
сгенерировать структурированные тестовые сценарии.

СТРОГИЕ ПРАВИЛА:

1. Используй только информацию, которая явно указана
   в переданных бизнес-требованиях.

2. Не придумывай бизнес-правила, которых нет в требованиях.

3. Не придумывай API endpoints, HTTP-методы, UI-элементы,
   поля, статусы, ограничения или поведение системы,
   если они не указаны в требованиях.

4. Каждый тестовый сценарий должен ссылаться
   только на существующий requirement_id.

5. Не изменяй исходный requirement_id.

6. Не добавляй requirement_id, которого нет
   в переданных бизнес-требованиях.

7. Не добавляй тестовые данные, которых нет
   в переданных бизнес-требованиях.

8. Не дублируй тестовые сценарии без необходимости.

9. Для каждого теста обязательно укажи:
   - id
   - requirement_id
   - title
   - description
   - priority
   - type
   - preconditions
   - steps
   - expected_result

10. priority MUST быть строкой и иметь
    только одно из следующих значений:

    "low"
    "medium"
    "high"
    "critical"

    Никогда не используй:
    1, 2, 3, 4
    "Low", "Medium", "High", "Critical"

11. type MUST быть одним из:

    "positive"
    "negative"
    "boundary"
    "validation"
    "security"
    "regression"

12. preconditions MUST всегда быть JSON-массивом.

    Если предварительные условия явно не указаны
    в требованиях, используй:

    "preconditions": []

13. steps MUST всегда быть JSON-массивом
    непустых строк.

14. expected_result MUST быть непустой строкой.

15. Не создавай пустые строки в:
    - title
    - description
    - steps
    - expected_result
    - preconditions

16. Позитивные, негативные, boundary, validation,
    security и regression сценарии создавай только тогда,
    когда они подтверждаются требованиями.

17. Не используй знания о системе,
    отсутствующие в переданных требованиях.

18. Верни только валидный JSON.

19. Не используй Markdown.

20. Не добавляй пояснения до или после JSON.

21. Корневой JSON-объект должен содержать
    только поле "test_cases".

22. Не добавляй дополнительные поля,
    отсутствующие в контракте.

Бизнес-требования:

{checklist}
""".strip()


REPAIR_PROMPT = """
Ты исправляешь JSON-контракт тестовых сценариев.

Предыдущий ответ LLM не прошёл JSON Schema validation.

СТРОГИЕ ПРАВИЛА:

1. Используй только исходные бизнес-требования.
2. Не придумывай новые требования.
3. Не изменяй requirement_id.
4. Используй только requirement_id из исходных требований.
5. Не добавляй тестовые данные, которых нет в требованиях.
6. Не придумывай API, UI, поля, параметры или бизнес-правила.
7. Не добавляй дополнительные поля.
8. Верни только JSON.
9. Не используй Markdown.
10. Корневой объект должен содержать только "test_cases".

КРИТИЧЕСКИ ВАЖНО:

priority MUST быть строкой:

"low"
"medium"
"high"
"critical"

Нельзя использовать числа.
Нельзя использовать "Low", "Medium", "High", "Critical".

preconditions MUST быть JSON-массивом.

Если предварительных условий нет в требованиях:

"preconditions": []

steps MUST быть непустым массивом непустых строк.

expected_result MUST быть непустой строкой.

Исправь ТОЛЬКО проблемы контракта.
Не добавляй новые сведения о системе.

ОБЯЗАТЕЛЬНЫЕ ТРЕБОВАНИЯ:

Каждый test_case обязан содержать:

"description":
непустая строка, описывающая проверяемое требование.

"expected_result":
непустая строка, описывающая ожидаемый результат.

Запрещено:

"description": ""

"expected_result": ""

Если информации недостаточно, используй:

"description":
"Verify requirement behavior."

"expected_result":
"System behavior matches requirement."

Не оставляй поля пустыми.

ИСХОДНЫЕ БИЗНЕС-ТРЕБОВАНИЯ:

{checklist}

ПРЕДЫДУЩИЙ ОТВЕТ:

{previous_response}

ОШИБКИ ВАЛИДАЦИИ:

{validation_errors}

Верни исправленный JSON без каких-либо пояснений.
""".strip()


class ScenarioGenerator:

    MAX_ATTEMPTS = 3

    def __init__(self, llm_client: LLMClient) -> None:
        self.llm_client = llm_client

    def generate(self,checklist: dict[str, Any]) -> dict[str, Any]:
        prompt = self._build_prompt(checklist)

        last_error: Exception | None = None

        for attempt in range(self.MAX_ATTEMPTS):
            response = self.llm_client.generate(prompt)

            try:
                contract = self._parse_response(response)

                validate_test_contract(contract)

                self._validate_requirement_ids(contract,checklist)

                self._validate_requirement_coverage(contract,checklist)

                return contract

            except (ValueError,TypeError,ContractValidationError) as exc:
                last_error = exc

                if attempt == self.MAX_ATTEMPTS - 1:
                    break

                prompt = self._build_repair_prompt(checklist=checklist, previous_response=response,validation_errors=str(exc))

        raise ContractValidationError("LLM failed to generate a valid test contract "f"after {self.MAX_ATTEMPTS} attempts. "f"Last error: {last_error}")

    @staticmethod
    def _build_prompt(checklist: dict[str, Any]) -> str:
        checklist_json = json.dumps(checklist,indent=2,ensure_ascii=False)

        return TEST_DESIGN_PROMPT.format(checklist=checklist_json)

    @staticmethod
    def _build_repair_prompt(checklist: dict[str, Any],previous_response: str,validation_errors: str) -> str:
        checklist_json = json.dumps(checklist,indent=2,ensure_ascii=False)

        return REPAIR_PROMPT.format(checklist=checklist_json,previous_response=previous_response,validation_errors=validation_errors)

    @staticmethod
    def _parse_response(response: str) -> dict[str, Any]:
        try:
            data = json.loads(response)

        except json.JSONDecodeError as exc:
            raise ValueError("LLM returned invalid JSON.") from exc

        if not isinstance(data, dict):
            raise TypeError("LLM response must be a JSON object.")

        return data

    @staticmethod
    def _validate_requirement_ids( contract: dict[str, Any],checklist: dict[str, Any]) -> None:
        requirements = checklist.get("requirements",[])

        allowed_ids: set[str] = set()

        for requirement in requirements:
            if not isinstance(requirement, dict):
                continue

            requirement_id = requirement.get("requirement_id")

            if not isinstance(requirement_id, str):
                requirement_id = requirement.get("id")

            if isinstance(requirement_id, str):
                allowed_ids.add(requirement_id)

        test_cases = contract.get("test_cases",[])

        for index, test_case in enumerate(test_cases):
            requirement_id = test_case.get("requirement_id")

            if requirement_id not in allowed_ids:
                raise ContractValidationError(
                    "Invalid requirement_id in generated "
                    f"test case [{index}]: "
                    f"{requirement_id!r}. "
                    f"Allowed values: {sorted(allowed_ids)}"
                )

    @staticmethod
    def _validate_requirement_coverage(contract: dict[str, Any],checklist: dict[str, Any]) -> None:
        requirements = checklist.get("requirements",[],)

        expected_ids: set[str] = set()

        for requirement in requirements:
            if not isinstance(requirement, dict):
                continue

            requirement_id = requirement.get("id")

            if not isinstance(requirement_id, str):
                requirement_id = requirement.get("requirement_id")

            if isinstance(requirement_id, str):expected_ids.add(requirement_id)

        generated_ids = {test_case.get("requirement_id") for test_case in contract.get("test_cases",[])}

        missing_ids = expected_ids - generated_ids

        if missing_ids:raise ContractValidationError("Missing test coverage for requirements: "f"{sorted(missing_ids)}")