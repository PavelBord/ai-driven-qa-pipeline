from playwright.sync_api import Page


class ProductPage:
    def __init__(self, page: Page):
        self.page = page
        self.product_title = page.locator(".product-title")
        self.add_to_cart_button = page.locator(".add-to-cart")
        self.product_price = page.locator(".product-price")
        self.product_description = page.locator(".product-description")

    def add_product_to_cart(self):
        """Добавляет продукт в корзину"""
        self.add_to_cart_button.click()
        return self

    def get_product_title(self) -> str:
        """Получает название продукта"""
        if not self.product_title.is_visible():
            return ""
        return self.product_title.text_content() or ""

    def get_product_price(self) -> str:
        """Получает цену продукта"""
        if not self.product_price.is_visible():
            return ""
        return self.product_price.text_content() or ""
