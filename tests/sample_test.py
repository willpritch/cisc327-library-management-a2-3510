def test_add_book_form_success(client):
    r = client.post(
        "/add_book",
        data={
            "title": "Test Book",
            "author": "Test Author",
            "isbn": "9780131103627",
            "total_copies": "1",  
            "copies": "1"          
        },
        follow_redirects=True,
    )
    assert r.status_code in (200, 302, 303)
    if r.status_code == 200:
        assert b"Test Book" in r.data
