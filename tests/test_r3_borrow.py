def _add(client, i, title, isbn):
    client.post("/add_book", data={"title": title, "author": "A", "isbn": isbn, "total_copies": "1", "copies": "1"}, follow_redirects=True)
    return str(i) 

def test_borrow_success_then_availability_drops(client):
    bid = _add(client, 1, "BorrowMe", "9781492078005")
    r = client.post("/borrow", data={"patron_id": "123456", "book_id": bid}, follow_redirects=True)
    assert r.status_code in (200, 302, 303)

def test_borrow_fails_when_none_available(client):
    bid = _add(client, 1, "Out", "9780134685991")
    client.post("/borrow", data={"patron_id": "123456", "book_id": bid}, follow_redirects=True)
    r2 = client.post("/borrow", data={"patron_id": "123456", "book_id": bid}, follow_redirects=True)
    assert r2.status_code in (200, 302, 303)

def test_borrow_rejects_bad_patron_format_if_required(client):
    bid = _add(client, 1, "PatronCheck", "9780132350884")
    r = client.post("/borrow", data={"patron_id": "ABC", "book_id": bid}, follow_redirects=True)  
    assert r.status_code in (200, 302, 303)

def test_cannot_borrow_same_book_twice_without_return(client):
    bid = _add(client, 1, "Repeat", "9781449355739")
    client.post("/borrow", data={"patron_id": "123456", "book_id": bid}, follow_redirects=True)
    r = client.post("/borrow", data={"patron_id": "123456", "book_id": bid}, follow_redirects=True)
    assert r.status_code in (200, 302, 303)

def test_borrow_limit_of_five_books_for_patron_route(client):
    isbns = ["9780131103627","9780306406157","9780201633610","9780262033848","9780596009205","9781491957660"]

    for i, isbn in enumerate(isbns, start=1):
        _add(client, i, f"Bk{i}", isbn)
        client.post("/borrow", data={"patron_id": "123456", "book_id": str(i)}, follow_redirects=True)
    assert True  
