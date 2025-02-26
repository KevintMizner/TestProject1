import re
from playwright.sync_api import Playwright, sync_playwright, expect


def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://allen.ymshub.com/login")
    page.get_by_placeholder("Username").click()
    page.get_by_placeholder("Username").fill("kthomas")
    page.get_by_placeholder("Username").press("Tab")
    page.get_by_placeholder("Password").fill("Password1!")
    page.get_by_role("button", name="Let's go").click()
    page.get_by_role("link", name=" Reports").click()
    page.get_by_role("link", name="CI Current Inventory").click()
    page.get_by_role("combobox", name="Building").click()
    page.get_by_role("button", name="Select All", exact=True).click()
    page.get_by_role("button", name="Show 100 rows▼").click()
    page.get_by_role("button", name="Show All").click()
    with page.expect_download() as download_info:
        page.get_by_role("button", name="CSV").click()
    download = download_info.value

    # ---------------------
    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)
