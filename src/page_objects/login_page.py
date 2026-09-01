from playwright.sync_api import Page


class LoginPage:
    def __init__(self, page: Page):
        self.page = page
        self.username_input = page.locator("#username")
        self.password_input = page.locator("#password")
        self.login_button = page.locator("#login-button")
        self.error_message = page.locator(".error-message")

    def login(self, username: str, password: str):
        """Выполняет вход пользователя"""
        self.username_input.fill(username)
        self.password_input.fill(password)
        self.login_button.click()
        return self

    def get_error_message(self) -> str:
        """Получает сообщение об ошибке"""
        if not self.error_message.is_visible():
            return ""
        return self.error_message.text_content() or ""
