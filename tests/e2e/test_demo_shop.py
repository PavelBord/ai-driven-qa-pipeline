from playwright.sync_api import Page, expect


def test_demo_web_shop_open(page: Page) -> None:
    page.goto(
        "https://demowebshop.tricentis.com"
    )

    expect(page).to_have_title("Demo Web Shop")

    expect(
        page.get_by_text(
            "Welcome to our store"
        )
    ).to_be_visible()