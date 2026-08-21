from __future__ import annotations

import json

from pipeline.llm.client import LLMClient


class MockLLMClient(LLMClient):

    def __init__(self) -> None:
        self.last_prompt = ""

    def generate(
        self,
        prompt: str,
        json_mode: bool = False,
    ) -> str:
        self.last_prompt = prompt

        if json_mode:
            return json.dumps(
                {
                    "test_cases": [
                        {
                            "id": "TC-001",
                            "requirement_id": "AUTH-001",
                            "title": "Successful authentication",
                            "description": (
                                "User authentication with valid credentials"
                            ),
                            "priority": "high",
                            "type": "positive",
                            "preconditions": [],
                            "steps": [
                                "Enter valid email",
                                "Enter valid password",
                                "Click login",
                            ],
                            "expected_result": (
                                "Authentication succeeds"
                            ),
                        },
                        {
                            "id": "TC-002",
                            "requirement_id": "AUTH-002",
                            "title": "Invalid password authentication",
                            "description": (
                                "Authentication with invalid password"
                            ),
                            "priority": "high",
                            "type": "negative",
                            "preconditions": [],
                            "steps": [
                                "Enter valid email",
                                "Enter invalid password",
                                "Click login",
                            ],
                            "expected_result": (
                                "Authentication fails"
                            ),
                        },
                        {
                            "id": "TC-003",
                            "requirement_id": "AUTH-003",
                            "title": "Empty credentials validation",
                            "description": (
                                "Authentication with empty fields"
                            ),
                            "priority": "medium",
                            "type": "negative",
                            "preconditions": [],
                            "steps": [
                                "Leave email empty",
                                "Leave password empty",
                                "Click login",
                            ],
                            "expected_result": (
                                "Validation error is displayed"
                            ),
                        },
                        {
                            "id": "TC-004",
                            "requirement_id": "AUTH-004",
                            "title": "Locked user authentication",
                            "description": (
                                "Authentication of locked user"
                            ),
                            "priority": "high",
                            "type": "negative",
                            "preconditions": [],
                            "steps": [
                                "Enter locked user credentials",
                                "Click login",
                            ],
                            "expected_result": (
                                "Access is denied"
                            ),
                        },
                        {
                            "id": "TC-005",
                            "requirement_id": "AUTH-005",
                            "title": "Session creation after login",
                            "description": (
                                "Verify user session creation"
                            ),
                            "priority": "medium",
                            "type": "positive",
                            "preconditions": [],
                            "steps": [
                                "Login successfully",
                                "Open user profile",
                            ],
                            "expected_result": (
                                "Active session is created"
                            ),
                        },
                    ]
                },
                ensure_ascii=False,
                indent=2,
            )

        return """
def test_TC_001():
    email = "<EMAIL>"
    password = "<PASSWORD>"
    pass
"""