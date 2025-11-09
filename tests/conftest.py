import pytest
from importlib import reload
import database
from services import library_service
from app import create_app  

@pytest.fixture()
def client():
    app = create_app()           
    app.config.update(TESTING=True)
    with app.test_client() as c:
        yield c

@pytest.fixture(autouse=True)
def reset_state():
    reload(database)
    reload(library_service)
