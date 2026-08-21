from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pipeline.contract_validator import (
    ContractValidationError,
    validate_test_contract,
)
from pipeline.llm.client import LLMClient

PROMPT_PATH = Path(
    "prompts/test-code-generation.txt"
)


def load_prompt() -> str:
    return PROMPT_PATH.read_text(
        encoding="utf-8"
    )


class CodeGenerator:

    def __init__(
        self,
        llm_client: LLMClient,
    ) -> None:

        self.llm_client = llm_client


    def generate(
        self,
        contract: dict[str, Any],
        requirements: list[dict[str, Any]] | None = None,
    ) -> str:

        validate_test_contract(
            contract
        )


        prompt = load_prompt().replace(
            "{contract}",
            json.dumps(
                {
                    "contract": contract,
                    "requirements": requirements or [],
                },
                indent=2,
                ensure_ascii=False,
            ),
        )


        code = self.llm_client.generate(
            prompt
        )


        code = code.replace(
            "-",
            "_",
        )


        print(
            "\n===== GENERATED CODE ====="
        )

        print(code)

        print(
            "==========================\n"
        )


        self._validate_test_code(
            contract,
            code,
        )


        return code


    @staticmethod
    def _validate_test_code(
        contract: dict[str, Any],
        code: str,
    ) -> None:


        if not code.strip():

            raise ContractValidationError(
                "Generated pytest code is empty"
            )


        if "def test_" not in code:

            raise ContractValidationError(
                "Generated code does not contain pytest function"
            )


        for test_case in contract.get(
            "test_cases",
            [],
        ):


            required_fields = {
                field
                for step in test_case.get(
                    "steps",
                    [],
                )
                for field in [
                    "email",
                    "password",
                ]
                if field in step.lower()
                and "empty" not in step.lower()
                and "invalid" not in step.lower()
            }


            for field in required_fields:

                if not any(
                    line.strip().startswith(
                        f"{field} ="
                    )
                    for line in code.splitlines()
                ):

                    raise ContractValidationError(
                        f"Missing required variable "
                        f"'{field}' for "
                        f"{test_case.get('requirement_id')}"
                    )