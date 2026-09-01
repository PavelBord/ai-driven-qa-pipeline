from __future__ import annotations

import json
import logging
from typing import Any

from pipeline.config import PROMPTS_DIR
from pipeline.llm.client import LLMClient

LOG = logging.getLogger(__name__)

PROMPT_PATH = PROMPTS_DIR / "code-review.txt"


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

        LOG.debug("Code review response: %s", response)

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