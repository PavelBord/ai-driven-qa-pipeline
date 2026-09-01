from unittest.mock import Mock

from page_objects.cart_page import CartPage
from page_objects.login_page import LoginPage
from page_objects.product_page import ProductPage


def test_login_page_initialization():
    """Тестируем инициализацию LoginPage."""
    mock_page = Mock()
    login_page = LoginPage(mock_page)
    assert login_page.page == mock_page


def test_product_page_initialization():
    """Тестируем инициализацию ProductPage."""
    mock_page = Mock()
    product_page = ProductPage(mock_page)
    assert product_page.page == mock_page


def test_cart_page_initialization():
    """Тестируем инициализацию CartPage."""
    mock_page = Mock()
    cart_page = CartPage(mock_page)
    assert cart_page.page == mock_page


def test_login_page_methods():
    """Тестируем методы LoginPage."""
    mock_page = Mock()
    login_page = LoginPage(mock_page)

    # Проверяем, что методы существуют
    assert hasattr(login_page, "login")
    assert hasattr(login_page, "get_error_message")


def test_product_page_methods():
    """Тестируем методы ProductPage."""
    mock_page = Mock()
    product_page = ProductPage(mock_page)

    # Проверяем, что методы существуют
    assert hasattr(product_page, "add_product_to_cart")
    assert hasattr(product_page, "get_product_title")
    assert hasattr(product_page, "get_product_price")


def test_cart_page_methods():
    """Тестируем методы CartPage."""
    mock_page = Mock()
    cart_page = CartPage(mock_page)

    # Проверяем, что методы существуют
    assert hasattr(cart_page, "checkout")
    assert hasattr(cart_page, "get_cart_item_count")
    assert hasattr(cart_page, "is_cart_empty")
    assert hasattr(cart_page, "get_total_amount")
