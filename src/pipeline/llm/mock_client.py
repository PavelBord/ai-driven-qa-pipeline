from __future__ import annotations

import json

from pipeline.llm.client import LLMClient


class MockLLMClient(LLMClient):
    def generate(self,_prompt: str,json_mode: bool = False) -> str:
        if json_mode:
            response = {
                "test_cases": [
                    {
                        "id": "TC-001",
                        "requirement_id": "AUTH-001",
                        "title": "Successful authentication",
                        "description": "User authentication",
                        "priority": "high",
                        "type": "positive",
                        "preconditions": [],
                        "steps": [
                            "Enter email",
                            "Enter password",
                        ],
                        "expected_result": (
                            "Authentication succeeds"
                        ),
                    }
                ]
            }

            return json.dumps(
                response,
                indent=2,
            )

        return """
def test_TC_001():
    email = "<EMAIL>"
    password = "<PASSWORD>"
    pass
"""