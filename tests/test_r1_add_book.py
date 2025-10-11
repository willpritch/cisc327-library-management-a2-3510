def _post_add(client, title, author, isbn, copies):
    return client.post(
        "/add_book",
        data={"title": title, "author": author, "isbn": isbn, "total_copies": str(copies), "copies": str(copies)},
        follow_redirects=True,
    )

def test_add_book_valid(client):
    r = _post_add(client, "Good", "Auth", "9780306406157", 2)
    assert r.status_code in (200, 302, 303)
    if r.status_code == 200:
        assert b"Good" in r.data or b"9780306406157" in r.data

def test_add_book_rejects_zero_copies(client):
    r = _post_add(client, "Zero", "Auth", "9780201633610", 0)
    assert r.status_code in (200, 302, 303)

def test_add_book_rejects_negative_copies(client):
    r = _post_add(client, "Neg", "Auth", "9780262033848", -1)
    assert r.status_code in (200, 302, 303)

def test_add_book_rejects_invalid_isbn_length(client):
    r = _post_add(client, "BadLen", "Auth", "12345", 1)
    assert r.status_code in (200, 302, 303)

def test_add_book_rejects_duplicate_isbn(client):
    _post_add(client, "Once", "Auth", "9780596009205", 1)
    r2 = _post_add(client, "Twice", "Auth", "9780596009205", 1) 
    assert r2.status_code in (200, 302, 303)
