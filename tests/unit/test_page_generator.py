from __future__ import annotations

from pipeline.page_objects.page_generator import PageGenerator


def test_to_module_name_converts_camel_case() -> None:
    assert PageGenerator.to_module_name("LoginPage") == "login_page"
    assert PageGenerator.to_module_name("ProductDetailsPage") == "product_details_page"


def test_to_module_name_lowercases_plain_names() -> None:
    assert PageGenerator.to_module_name("Home") == "home"