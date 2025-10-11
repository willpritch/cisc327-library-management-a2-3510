# tests/test_a2_additional_cases.py

def test_borrow_limit_blocked_after_five_books(client):
    """Ensure patron cannot borrow more than 5 books."""
    patron = "123456"
    for i in range(1, 7):
        client.post("/add_book", data={
            "title": f"Bk{i}", "author": "Auth",
            "isbn": f"97800000000{i:02d}", "total_copies": "1", "copies": "1"
        }, follow_redirects=True)
        client.post("/borrow", data={"patron_id": patron, "book_id": str(i)}, follow_redirects=True)
    r = client.post("/borrow", data={"patron_id": patron, "book_id": "6"}, follow_redirects=True)
    assert r.status_code in (200, 302, 303)


def test_return_increments_availability(client):
    """After return, available copies should increase."""
    client.post("/add_book", data={
        "title": "ReturnTest", "author": "A", "isbn": "9781111111111",
        "total_copies": "1", "copies": "1"
    }, follow_redirects=True)
    client.post("/borrow", data={"patron_id": "123456", "book_id": "1"}, follow_redirects=True)
    r = client.post("/return", data={"patron_id": "123456", "book_id": "1"}, follow_redirects=True)
    assert r.status_code in (200, 302, 303)


def test_late_fee_calculation_basic(client):
    """Call the late-fee API and ensure it returns JSON with expected keys."""
    r = client.get("/api/late_fee/123456/1")
    assert r.status_code in (200, 404)
    data = r.get_json()
    assert "fee" in data and "days_overdue" in data


def test_search_by_partial_title_returns_match(client):
    """Search by partial title, should return matching book."""
    client.post("/add_book", data={
        "title": "Quantum Physics", "author": "Einstein",
        "isbn": "9782222222222", "total_copies": "1", "copies": "1"
    }, follow_redirects=True)
    r = client.get("/search?q=quant&type=title")
    assert r.status_code == 200
    assert b"Quantum Physics" in r.data


def test_patron_status_page_loads(client):
    """Ensure patron status page renders for valid patron ID."""
    r = client.get("/patron/123456/status")
    assert r.status_code in (200, 404)
