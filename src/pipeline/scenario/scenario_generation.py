from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pipeline.contract_validator import ContractValidationError, validate_test_contract
from pipeline.llm.client import LLMClient

PROMPT_PATH = Path("prompts/test-scenario-generation.txt")


def load_prompt() -> str:
    return PROMPT_PATH.read_text(
        encoding="utf-8"
    )


class ScenarioGenerator:

    MAX_ATTEMPTS = 3

    def __init__(
        self,
        llm_client: LLMClient,
    ) -> None:
        self.llm_client = llm_client

    def generate(
        self,
        checklist: dict[str, Any],
    ) -> dict[str, Any]:

        prompt = self._build_prompt(
            checklist
        )

        last_error: Exception | None = None

        for attempt in range(
            self.MAX_ATTEMPTS
        ):

            response = self.llm_client.generate(
                prompt
            )

            try:

                contract = self._parse_response(
                    response
                )

                validate_test_contract(
                    contract
                )

                self._validate_requirement_ids(
                    contract,
                    checklist,
                )

                self._validate_requirement_coverage(
                    contract,
                    checklist,
                )

                return contract


            except (
                ValueError,
                TypeError,
                ContractValidationError,
            ) as exc:

                last_error = exc

                if attempt == self.MAX_ATTEMPTS - 1:
                    break

                prompt = self._build_prompt(
                    checklist
                )


        raise ContractValidationError(
            f"Failed to generate valid test contract "
            f"after {self.MAX_ATTEMPTS} attempts. "
            f"Last error: {last_error}"
        )


    @staticmethod
    def _build_prompt(
        checklist: dict[str, Any],
    ) -> str:

        return load_prompt().replace(
            "{checklist}",
            json.dumps(
                checklist,
                indent=2,
                ensure_ascii=False,
            ),
        )


    @staticmethod
    def _parse_response(
        response: str,
    ) -> dict[str, Any]:

        try:

            data = json.loads(
                response
            )


        except json.JSONDecodeError as exc:

            raise ValueError(
                "LLM returned invalid JSON"
            ) from exc


        if not isinstance(
            data,
            dict,
        ):

            raise TypeError(
                "LLM response must be JSON object"
            )


        return data


    @staticmethod
    def _extract_requirement_id(
        requirement: dict[str, Any],
    ) -> str | None:

        value = (
            requirement.get("id")
            or requirement.get("requirement_id")
        )

        if isinstance(
            value,
            str,
        ):
            return value

        return None


    @classmethod
    def _validate_requirement_ids(
        cls,
        contract: dict[str, Any],
        checklist: dict[str, Any],
    ) -> None:

        allowed_ids: set[str] = {
            requirement_id
            for requirement in checklist.get(
                "requirements",
                [],
            )
            if isinstance(
                requirement,
                dict,
            )
            for requirement_id in [
                cls._extract_requirement_id(
                    requirement
                )
            ]
            if requirement_id is not None
        }


        for index, test_case in enumerate(
            contract.get(
                "test_cases",
                [],
            )
        ):

            requirement_id = test_case.get(
                "requirement_id"
            )


            if requirement_id not in allowed_ids:

                raise ContractValidationError(
                    f"Invalid requirement_id in test case "
                    f"[{index}]: {requirement_id}"
                )


    @classmethod
    def _validate_requirement_coverage(
        cls,
        contract: dict[str, Any],
        checklist: dict[str, Any],
    ) -> None:

        expected_ids: set[str] = {
            requirement_id
            for requirement in checklist.get(
                "requirements",
                [],
            )
            if isinstance(
                requirement,
                dict,
            )
            for requirement_id in [
                cls._extract_requirement_id(
                    requirement
                )
            ]
            if requirement_id is not None
        }


        generated_ids: set[str | None] = {
            test_case.get(
                "requirement_id"
            )
            for test_case in contract.get(
                "test_cases",
                [],
            )
        }


        missing = expected_ids - generated_ids


        if missing:

            raise ContractValidationError(
                f"Missing test coverage: "
                f"{sorted(missing)}"
            )