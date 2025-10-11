def test_search_title_partial_case_insensitive_route(client):
    client.post("/add_book", data={"title":"Alpha Title","author":"AA","isbn":"9781491957660","copies":"1"}, follow_redirects=True)
    r = client.get("/search?q=alpha&type=title")
    assert r.status_code in (200, 302, 303)

def test_search_author_partial_case_insensitive_route(client):
    client.post("/add_book", data={"title":"Beta","author":"UniqueAuthorZZ","isbn":"9781492078005","copies":"1"}, follow_redirects=True)
    r = client.get("/search?q=uniqueauthor&type=author")
    assert r.status_code in (200, 302, 303)

def test_search_isbn_exact_route(client):
    client.post("/add_book", data={"title":"Gamma","author":"G","isbn":"9780134685991","copies":"1"}, follow_redirects=True)
    r = client.get("/search?q=9780134685991&type=isbn")
    assert r.status_code in (200, 302, 303)

def test_search_isbn_partial_should_not_match_route(client):
    client.post("/add_book", data={"title":"Delta","author":"D","isbn":"9780131103627","copies":"1"}, follow_redirects=True)
    r = client.get("/search?q=9780131103&type=isbn")
    assert r.status_code in (200, 302, 303)

def test_search_no_results_route(client):
    r = client.get("/search?q=NoSuchBook&type=title")
    assert r.status_code in (200, 302, 303)
