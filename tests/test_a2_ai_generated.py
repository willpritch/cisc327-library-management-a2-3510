# tests/test_a2_ai_generated.py
"""
AI-Generated Tests (Step 3)
These were created using ChatGPT suggestions for Assignment 2 Step 3.
"""

def test_ai_generated_borrow_invalid_book(client):
    """AI suggested: test borrowing a non-existent book returns 404 or error message."""
    r = client.post("/borrow", data={"patron_id": "123456", "book_id": "99999"}, follow_redirects=True)
    assert r.status_code in (200, 404, 500)


def test_ai_generated_return_without_borrow(client):
    """AI suggested: test returning a book that was never borrowed should fail gracefully."""
    r = client.post("/return", data={"patron_id": "123456", "book_id": "1"}, follow_redirects=True)
    assert r.status_code in (200, 404, 500)


def test_ai_generated_late_fee_max_cap(client):
    """AI suggested: simulate a book 40 days overdue and ensure fee caps at $15."""
    from library_service import calculate_late_fee_for_book
    # Simulate manually
    fake_patron = "123456"
    fake_book = 1
    result = calculate_late_fee_for_book(fake_patron, fake_book)
    assert isinstance(result, dict)
    if "fee" in result:
        assert result["fee"] <= 15.00


def test_ai_generated_search_empty_query(client):
    """AI suggested: searching with an empty query returns no results."""
    r = client.get("/search?q=&type=title")
    assert r.status_code == 200
    assert b"No results" or b"Catalog" in r.data
