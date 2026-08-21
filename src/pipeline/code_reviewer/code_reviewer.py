from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pipeline.llm.client import LLMClient

PROMPT_PATH = Path("prompts/code-review.txt")


class CodeReviewer:

    def __init__(
        self,
        llm_client: LLMClient,
    ) -> None:

        self.llm_client = llm_client


    def review(
        self,
        code: str,
    ) -> dict[str, Any]:

        prompt = (
            PROMPT_PATH
            .read_text(
                encoding="utf-8"
            )
            .replace(
                "{code}",
                code,
            )
        )

        response = self.llm_client.generate(
            prompt
        )

        print("\n===== CODE REVIEW RESPONSE =====")
        print(response)
        print("================================\n")

        return self._parse_response(
            response
        )


    @staticmethod
    def _parse_response(
        response: str,
    ) -> dict[str, Any]:

        if not response.strip():

            return {
                "status": "failed",
                "issues": [
                    "Empty AI response"
                ],
            }


        try:

            data = json.loads(
                response
            )


        except json.JSONDecodeError:


            return {
                "status": "failed",
                "issues": [
                    "AI returned non JSON response",
                    response,
                ],
            }


        if not isinstance(
            data,
            dict,
        ):

            return {
                "status": "failed",
                "issues": [
                    "AI review must be JSON object"
                ],
            }


        return data