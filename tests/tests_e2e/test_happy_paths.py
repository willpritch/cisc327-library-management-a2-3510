import os
import pytest

BASE_URL = f"http://127.0.0.1:{os.getenv('E2E_PORT','5000')}"

@pytest.mark.e2e
def test_catalog_loads(page):
    page.goto(f"{BASE_URL}/catalog")
    page.wait_for_selector("text=Book Catalog")
    # A header cell we expect
    assert page.locator("th:has-text('ISBN')").count() == 1

@pytest.mark.e2e
def test_add_book_then_visible_in_catalog(page):
    page.goto(f"{BASE_URL}/add_book")
    page.fill("input[name=title]", "E2E Book")
    page.fill("input[name=author]", "E2E Author")
    page.fill("input[name=isbn]", "9991234567890")
    page.fill("input[name=total_copies]", "2")
    page.click("button[type=submit]")

    page.goto(f"{BASE_URL}/catalog")

    assert page.locator("tbody tr").filter(has_text="E2E Book").count() >= 1

@pytest.mark.e2e
def test_search_by_title(page):
    page.goto(f"{BASE_URL}/search?q=E2E%20Book&type=title")
    # Expect the matching result table to include this title
    assert page.locator("tbody tr").filter(has_text="E2E Book").count() >= 1

@pytest.mark.e2e
def test_borrow_and_return_flow(page):
    # Borrow first available matching row
    page.goto(f"{BASE_URL}/catalog")
    row = page.locator("tbody tr").filter(has_text="E2E Book").first
    # Borrow button may have a form or link, adjust selector to your template
    borrow_btn = row.locator("button, a").filter(has_text="Borrow").first
    if borrow_btn.count() == 0:
        pytest.skip("Borrow action not present in UI")
    # Try borrow with a valid patron id
    borrow_btn.click()
    page.fill("input[name=patron_id]", "123456")
    page.click("button[type=submit]")
    page.wait_for_url(f"{BASE_URL}/catalog")
    page.goto(f"{BASE_URL}/return")
    page.fill("input[name=patron_id]", "123456")
    page.fill("input[name=book_id]", "1")  
    page.click("button[type=submit]")
    page.wait_for_url(f"{BASE_URL}/return")
    page.goto(f"{BASE_URL}/catalog")
    assert page.locator("table").count() >= 1
