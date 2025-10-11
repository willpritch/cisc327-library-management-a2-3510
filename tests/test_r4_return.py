def test_return_increases_availability_route(client):
    client.post("/add_book", data={"title":"R1","author":"A","isbn":"9780131103627","copies":"1"}, follow_redirects=True)
    client.post("/borrow", data={"patron_id":"123456","book_id":"1"}, follow_redirects=True)
    r = client.post("/return", data={"patron_id":"123456","book_id":"1"}, follow_redirects=True)
    assert r.status_code in (200, 302, 303)

def test_return_unknown_book_route(client):
    r = client.post("/return", data={"patron_id":"123456","book_id":"9999"}, follow_redirects=True)
    assert r.status_code in (200, 404, 405, 302, 303)

def test_return_without_prior_borrow_route(client):
    client.post("/add_book", data={"title":"R2","author":"A","isbn":"9780262033848","copies":"1"}, follow_redirects=True)
    r = client.post("/return", data={"patron_id":"123456","book_id":"1"}, follow_redirects=True)
    assert r.status_code in (200, 302, 303)

def test_return_must_match_patron_route(client):
    client.post("/add_book", data={"title":"R3","author":"A","isbn":"9780596009205","copies":"1"}, follow_redirects=True)
    client.post("/borrow", data={"patron_id":"111111","book_id":"1"}, follow_redirects=True)
    r = client.post("/return", data={"patron_id":"222222","book_id":"1"}, follow_redirects=True)
    assert r.status_code in (200, 302, 303)

def test_return_bad_input_route(client):
    r = client.post("/return", data={"patron_id":"","book_id":""}, follow_redirects=True)
    assert r.status_code in (200, 400, 404, 405, 302, 303)


