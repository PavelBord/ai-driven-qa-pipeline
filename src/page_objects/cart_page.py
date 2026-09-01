from playwright.sync_api import Page


class CartPage:
    def __init__(self, page: Page):
        self.page = page
        self.cart_items = page.locator(".cart-item")
        self.checkout_button = page.locator(".checkout-button")
        self.empty_cart_message = page.locator(".empty-cart")
        self.total_amount = page.locator(".total-amount")

    def checkout(self):
        """Переходит к оформлению заказа"""
        self.checkout_button.click()
        return self

    def get_cart_item_count(self) -> int:
        """Получает количество товаров в корзине"""
        return self.cart_items.count()

    def is_cart_empty(self) -> bool:
        """Проверяет, пуста ли корзина"""
        return self.empty_cart_message.is_visible()

    def get_total_amount(self) -> str:
        """Получает общую сумму"""
        if not self.total_amount.is_visible():
            return ""
        return self.total_amount.text_content() or ""
