from fastapi.testclient import TestClient
from pymongo import MongoClient
from jose import JWTError, jwt
#from urllib import urlencode
from ..main import app
import pytest
import os

class AuthTestClient:
    test_client = None
    test_db = None

client = TestClient(app)

@pytest.fixture(scope="module")
def setup():
    with TestClient(app) as client:
        AuthTestClient.test_client = client

        yield AuthTestClient


def test_create_valid_token(setup):
    auth_test_client = setup
    response = auth_test_client.test_client.post(
        '/token',
        {
            "username" : "johndoe",
            "password" : "secret"
        }
    )

    assert response.status_code == 200
    assert response.json()['token_type'] == "bearer"

    payload = jwt.decode(
        response.json()['access_token'],
        os.environ['AUTH_SECRET_KEY'],
        algorithms=[os.environ['AUTH_ALGORITHM']]
    )

    assert payload.get("sub") == "johndoe"

def test_fail_to_create_token_with_invalid_credentails(setup):
    auth_test_client = setup
    response = auth_test_client.test_client.post(
        '/token',
        {
            "username" : "someperson",
            "password" : "not_a_password"
        }
    )

    assert response.status_code == 401
    assert response.json()['detail'] == "Incorrect username or password"

def test_fail_to_create_token_with_disabled_user(setup):
    auth_test_client = setup
    response = auth_test_client.test_client.post(
        '/token',
        {
            "username" : "janedoe",
            "password" : "secret"
        }
    )

    assert response.status_code == 400
    assert response.json()['detail'] == "Inactive user"
