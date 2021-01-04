from fastapi.testclient import TestClient
from ..main import app
import pytest

client = TestClient(app)

@pytest.fixture(scope="module")
def setup():
    print("This should be called once.")
    client = TestClient(app)
    return client

def test_read_main(setup):
    client = setup
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message" : "Hello World"}
