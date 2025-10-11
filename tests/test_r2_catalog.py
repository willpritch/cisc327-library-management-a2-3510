def test_catalog_shows_added_item(client):
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
    page = r.data
    assert (b"Shown" in page) or (b"9780306406157" in page)

