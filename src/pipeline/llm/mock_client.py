from __future__ import annotations

import ast
import json

from pipeline.llm.client import LLMClient


class MockLLMClient(LLMClient):

    def __init__(self) -> None:
        self.last_prompt = ""

    @staticmethod
    def _is_page_object_prompt(
        prompt: str,
    ) -> bool:
        # Page-object промпты имеют маркеры "Страница:" и "Элементы:",
        # тогда как промпты кодогенерации использют "TEST CONTRACT:" / "PAGE OBJECTS".
        return (
            "Страница:" in prompt
            and "Элементы:" in prompt
        )

    @staticmethod
    def _extract_name(
        prompt: str,
        start_marker: str,
        end_marker: str | None = None,
    ) -> str:

        if start_marker not in prompt:
            return ""

        block = prompt.split(
            start_marker,
            1,
        )[1]

        if end_marker and end_marker in block:
            block = block.split(
                end_marker,
                1,
            )[0]

        return block.strip()

    def _generate_page_object(
        self,
        prompt: str,
    ) -> str:

        page_name = self._extract_name(
            prompt,
            "Страница:",
            "Описание:",
        )

        if not page_name:
            page_name = "Page"

        elements_raw = self._extract_name(
            prompt,
            "Элементы:",
        )

        elements: dict[str, dict[str, str]] = {}

        if elements_raw:
            try:
                elements = ast.literal_eval(
                    elements_raw
                )
            except (ValueError, SyntaxError):
                elements = {}

        lines = [
            "from playwright.sync_api import Page",
            "",
            "",
            f"class {page_name}:",
            "",
            "    def __init__(",
            "        self,",
            "        page: Page,",
            "    ) -> None:",
            "",
            "        self.page = page",
            "",
        ]

        for name, attrs in elements.items():
            if not isinstance(
                attrs,
                dict,
            ):
                # Элемент без структуры (например, маскированное PII
                # значение "<PASSWORD>") — не можем вывести локатор.
                continue

            locator = attrs.get(
                "locator",
                "",
            )
            if not locator:
                continue

            const = (
                name.upper()
            )
            lines.append(
                f"    {const}_LOCATOR = {locator!r}"
            )

        if elements:
            lines.append("")

        for name, attrs in elements.items():
            if not isinstance(
                attrs,
                dict,
            ):
                continue

            if not attrs.get(
                "locator",
                "",
            ):
                continue

            lines.append(
                f"    def click_{name}("
                "self"
                ") -> None:"
            )
            lines.append(
                "        self.page.click("
                f"self.{name.upper()}_LOCATOR"
                ")"
            )
            lines.append("")

        return "\n".join(
            lines
        )

    def _generate_test_code(
        self,
        prompt: str,
    ) -> str:

        contract_raw = self._extract_name(
            prompt,
            "TEST CONTRACT:",
            "AVAILABLE PAGE OBJECTS:",
        )

        test_id = "TC_001"

        if contract_raw:
            try:
                contract = json.loads(
                    contract_raw
                )
                test_id = contract.get(
                    "id",
                    test_id,
                ).replace(
                    "-",
                    "_",
                )
            except json.JSONDecodeError:
                test_id = (
                    "TC_001"
                )

        return (
            f"def test_{test_id}(page):"
            "\n"
            "    assert True"
            "\n"
        )

    @staticmethod
    def _generate_code_review() -> str:
        return json.dumps(
            {
                "status": "passed",
                "issues": [],
                "recommendations": [],
            },
        )

    @staticmethod
    def _generate_bug_report() -> str:
        return json.dumps(
            {
                "title": "Mock bug report",
                "severity": "medium",
                "priority": "medium",
                "description": (
                    "AI code review failed "
                    "for the generated test"
                ),
                "steps_to_reproduce": [
                    "Run pytest",
                    "Observe failure",
                ],
                "expected_result": (
                    "Test passes"
                ),
                "actual_result": (
                    "Test fails"
                ),
            },
        )

    def generate(
        self,
        prompt: str,
        json_mode: bool = False,
    ) -> str:

        self.last_prompt = prompt
        if self._is_page_object_prompt(prompt):
            return self._generate_page_object(prompt)

        if "КОД ДЛЯ ПРОВЕРКИ:" in prompt:
            return self._generate_code_review()

        if "AI анализ:" in prompt:
            return self._generate_bug_report()

        if json_mode:
            return json.dumps(
                {
                    "test_cases": [
                        {
                            "id": "TC-USER-001",
                            "requirement_id": "USER-001",
                            "title": "User registration",
                            "description": (
                                "User can register "
                                "a new account"
                            ),
                            "priority": "high",
                            "type": "positive",
                            "preconditions": [],
                            "steps": [
                                "Open registration page",
                                "Fill registration form",
                                "Submit registration",
                            ],
                            "expected_result": (
                                "New user account "
                                "is created"
                            ),
                        },
                        {
                            "id": "TC-USER-002",
                            "requirement_id": "USER-002",
                            "title": "Successful login",
                            "description": (
                                "User can login "
                                "with valid credentials"
                            ),
                            "priority": "high",
                            "type": "positive",
                            "preconditions": [],
                            "steps": [
                                "Open login page",
                                "Enter credentials",
                                "Click login button",
                            ],
                            "expected_result": (
                                "User is logged in"
                            ),
                        },
                        {
                            "id": "TC-USER-003",
                            "requirement_id": "USER-003",
                            "title": "Invalid login",
                            "description": (
                                "User cannot login "
                                "with invalid credentials"
                            ),
                            "priority": "high",
                            "type": "negative",
                            "preconditions": [],
                            "steps": [
                                "Open login page",
                                "Enter invalid credentials",
                                "Click login button",
                            ],
                            "expected_result": (
                                "Error message displayed"
                            ),
                        },
                        {
                            "id": "TC-PRODUCT-001",
                            "requirement_id": "PRODUCT-001",
                            "title": "Search product",
                            "description": (
                                "User can search products"
                            ),
                            "priority": "medium",
                            "type": "positive",
                            "preconditions": [],
                            "steps": [
                                "Open catalog",
                                "Search product",
                            ],
                            "expected_result": (
                                "Products displayed"
                            ),
                        },
                        {
                            "id": "TC-PRODUCT-002",
                            "requirement_id": "PRODUCT-002",
                            "title": "Open product details",
                            "description": (
                                "User can open product page"
                            ),
                            "priority": "medium",
                            "type": "positive",
                            "preconditions": [],
                            "steps": [
                                "Select product",
                            ],
                            "expected_result": (
                                "Product page displayed"
                            ),
                        },
                        {
                            "id": "TC-CART-001",
                            "requirement_id": "CART-001",
                            "title": "Add product to cart",
                            "description": (
                                "User can add product"
                            ),
                            "priority": "high",
                            "type": "positive",
                            "preconditions": [],
                            "steps": [
                                "Open product",
                                "Click add to cart",
                            ],
                            "expected_result": (
                                "Product added to cart"
                            ),
                        },
                        {
                            "id": "TC-CART-002",
                            "requirement_id": "CART-002",
                            "title": "Update cart quantity",
                            "description": (
                                "User can update quantity"
                            ),
                            "priority": "medium",
                            "type": "positive",
                            "preconditions": [],
                            "steps": [
                                "Open cart",
                                "Change quantity",
                            ],
                            "expected_result": (
                                "Cart updated"
                            ),
                        },
                        {
                            "id": "TC-CART-003",
                            "requirement_id": "CART-003",
                            "title": "Remove product",
                            "description": (
                                "User can remove product"
                            ),
                            "priority": "medium",
                            "type": "positive",
                            "preconditions": [],
                            "steps": [
                                "Open cart",
                                "Remove product",
                            ],
                            "expected_result": (
                                "Product removed"
                            ),
                        },
                        {
                            "id": "TC-ORDER-001",
                            "requirement_id": "ORDER-001",
                            "title": "Complete checkout",
                            "description": (
                                "User can complete checkout"
                            ),
                            "priority": "high",
                            "type": "positive",
                            "preconditions": [],
                            "steps": [
                                "Open cart",
                                "Proceed checkout",
                            ],
                            "expected_result": (
                                "Order created"
                            ),
                        },
                        {
                            "id": "TC-ORDER-002",
                            "requirement_id": "ORDER-002",
                            "title": "Order confirmation",
                            "description": (
                                "User receives confirmation"
                            ),
                            "priority": "high",
                            "type": "positive",
                            "preconditions": [],
                            "steps": [
                                "Complete checkout",
                            ],
                            "expected_result": (
                                "Confirmation displayed"
                            ),
                        },
                    ]
                },
                indent=2,
                ensure_ascii=False,
            )

        return self._generate_test_code(prompt)
