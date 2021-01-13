from fastapi.testclient import TestClient
from pymongo import MongoClient
from jose import jwt
from ..main import app
from datetime import datetime
import pytest
import os

class AuthTestClient:
    test_client = None
    test_db = None

##########################################################################
### FIXTURES
##########################################################################

@pytest.fixture(scope="module")
def setup():
    with TestClient(app) as client:
        AuthTestClient.test_client = client

        URI = os.environ['TEST_MONGODB_URI']
        if URI is None:
            print("TEST_MONGODB_URI is not defined!")
            assert 0

        client = MongoClient(URI)

        db = client.get_default_database()

        ## 1. Ensure db is in 'dev' database.
        ## No testing in production
        if db.name == 'dev':
            AuthTestClient.test_db = db
            yield AuthTestClient

        else:
            print("Not in the 'dev' database! Exiting!")
            assert 0

@pytest.fixture()
def populate_valid_user(setup):
    auth_test_client = setup

    user = AuthTestClient.test_db.users.find_one(
        { "_id" : "test_auth_valid_user" }
    )
    result = AuthTestClient.test_db.users.find_one_and_update(
        {
            "_id" : "test_auth_valid_user"
        },
        {
            "$set" : {
                "username" : "test_auth_valid_user",
                "email" : "test_auth_valid_user@test.com",
                "password_hash" : "$2b$12$.IWgqTmhx0qtw6oB/JTdGeephe7xaWMNeE.WEoxiMQiW5KbnfmsE2",
                "enabled" : True,
                "creation_date" : datetime.now()
            }
        },
        upsert=True
    )

    return auth_test_client

@pytest.fixture()
def populate_disabled_user(setup):
    auth_test_client = setup

    result = AuthTestClient.test_db.users.find_one_and_update(
        {
            "_id" : "test_auth_disabled_user"
        },
        {
            "$set" : {
                "username" : "test_auth_disabled_user",
                "email" : "test_auth_disabled_user@test.com",
                "password_hash" : "$2b$12$.IWgqTmhx0qtw6oB/JTdGeephe7xaWMNeE.WEoxiMQiW5KbnfmsE2",
                "enabled" : False,
                "creation_date" : datetime.now()
            }
        },
        upsert=True
    )

    return auth_test_client

##########################################################################
### TESTS
##########################################################################

def test_create_valid_token(populate_valid_user):
    auth_test_client = populate_valid_user
    response = auth_test_client.test_client.post(
        '/token',
        {
            "username" : "test_auth_valid_user",
            "password" : "test"
        }
    )

    assert response.status_code == 200
    assert response.json()['token_type'] == "bearer"

    payload = jwt.decode(
        response.json()['access_token'],
        os.environ['AUTH_SECRET_KEY'],
        algorithms=[os.environ['AUTH_ALGORITHM']]
    )

    assert payload.get("sub") == "test_auth_valid_user"

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

def test_fail_to_create_token_with_disabled_user(populate_disabled_user):
    auth_test_client = populate_disabled_user
    response = auth_test_client.test_client.post(
        '/token',
        {
            "username" : "test_auth_disabled_user",
            "password" : "test"
        }
    )

    assert response.status_code == 400
    assert response.json()['detail'] == "Inactive user"
