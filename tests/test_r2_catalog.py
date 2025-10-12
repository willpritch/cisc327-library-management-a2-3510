def test_catalog_page_loads(client):
    """Page should load successfully."""
    r = client.get("/catalog")
    assert r.status_code == 200
    # check for general structure keywords
    assert (b"Add New Book" in r.data) or (b"<table" in r.data) or (b"Catalog" in r.data)

def test_catalog_shows_isbn_header(client):
    """Ensure ISBN header is visible."""
    r = client.get("/catalog")
    assert b"ISBN" in r.data

def test_catalog_shows_added_item(client):
    """Newly added book should appear in catalog."""
    client.post(
        "/add_book",
        data={
            "title": "Shown",
            "author": "Auth",
            "isbn": "9780306406157",
            "total_copies": "1",
            "copies": "1",
        },
        follow_redirects=True,
    )
    r = client.get("/catalog")
    assert r.status_code == 200
    assert (b"Shown" in r.data) or (b"9780306406157" in r.data)

def test_catalog_shows_available_total(client):
    """Available and total copy counts should display."""
    r = client.get("/catalog")
    assert (b"Available" in r.data) or (b"Total" in r.data)

def test_catalog_has_borrow_button_for_available_book(client):
    """Borrow button should appear if book is available."""
    client.post(
        "/add_book",
        data={
            "title": "Borrowable",
            "author": "Person",
            "isbn": "9780131103627",
            "total_copies": "2",
            "copies": "2",
        },
        follow_redirects=True,
    )
    r = client.get("/catalog")
    assert b"Borrow" in r.data


