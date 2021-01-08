
from fastapi.testclient import TestClient
from ..main import app
from datetime import datetime
from pymongo import MongoClient
import pytest
import os

## Configuring tests to run in order for the time being.
## Need to figure out how to do pre-test setup and post-test teardown
## Example: need to populate documents to verify get / delete is working

class UserTestClient:
    test_client = None
    test_db = None

##########################################################################
### FIXTURES
##########################################################################

@pytest.fixture(scope="module")
def setup():
    with TestClient(app) as client:
        # Create a single test client that we use throughout all tests
        UserTestClient.test_client = client

        URI = os.environ['TEST_MONGODB_URI']
        if URI is None:
            print("TEST_MONGODB_URI is not defined!")
            assert 0

        client = MongoClient(URI)

        db = client.get_default_database()

        ## 1. Ensure db is in 'dev' database.
        ## No testing in production
        if db.name == 'dev':
            db.drop_collection("users")

            UserTestClient.test_db = db
            yield UserTestClient

        else:
            print("Not in the 'dev' database! Exiting!")
            assert 0

@pytest.fixture(scope="function")
def populate_gettable_user(setup):
    user_test_client = setup

    result = UserTestClient.test_db.users.insert_one({
        "_id" : "100",
        "username" : "test",
        "email" : "test@test.com",
        "password_hash" : "dummyhashedpassword",
        "enabled" : True,
        "creation_date" : datetime.now()
    })

    return user_test_client

@pytest.fixture(scope="function")
def populate_existing_username_user(setup):
    user_test_client = setup

    user = UserTestClient.test_db.users.insert_one({
        "_id" : "test_create_existing_username_user",
        "username": "test_existing_username",
        "email": "test_existing_username@testing.com",
        "password_hash" : "dummyhashedpassword",
        "enabled": True,
        "client_hash" : "abcdefgh123456789",
        "creation_date" : datetime.now()
    })

    return user_test_client

@pytest.fixture(scope="function")
def populate_existing_email_user(setup):
    user_test_client = setup

    user = UserTestClient.test_db.users.insert_one({
        "_id" : "test_create_existing_email_user",
        "username": "testing_existing_email",
        "email": "test_existing_email@testing.com",
        "password_hash" : "dummyhashedpassword",
        "enabled": True,
        "client_hash" : "abcdefgh123456789",
        "creation_date" : datetime.now()
    })

    return user_test_client

@pytest.fixture(scope="function")
def populate_removeable_user(setup):
    user_test_client = setup

    user = UserTestClient.test_db.users.insert_one({
        "_id" : "test_delete_user",
        "username" : "test-delete-user",
        "email" : "test-delete-user@testing.com",
        "password_hash" : "dummyhashedpassword",
        "enabled" : True,
        "creation_date" : datetime.now()
    })

    return user_test_client

##########################################################################
### TESTS
##########################################################################
def test_get_user(populate_gettable_user):
    user_test_client = populate_gettable_user
    response = user_test_client.test_client.get(
        '/users/100'
    )

    assert response.status_code == 200

    response_body = response.json()
    assert response_body['username'] == "test"
    assert response_body['email'] == "test@test.com"
    assert response_body['enabled'] == True

def test_get_nonexistent_user(setup):
    user_test_client = setup
    response = user_test_client.test_client.get(
        '/users/200'
    )

    assert response.status_code == 404
    assert response.json() == { "detail" : "User not found." }

def test_create_user(setup):
    user_test_client = setup
    response = user_test_client.test_client.post(
        '/users/',
        json={
            "username": "TESTING-test_create_user",
            "email": "test_create_user@testing.com",
            "enabled": True,
            "client_hash" : "abcdefgh123456789"
        }
    )
    assert response.status_code == 200
    assert response.json() is not None

def test_create_user_wont_set_password_hash(setup):
    user_test_client = setup
    response = user_test_client.test_client.post(
        '/users/',
        json={
            "username": "TESTING-test_set_password_hash",
            "email": "test_set_password_hash@testing.com",
            "enabled": True,
            "client_hash" : "abcdefgh123456789",
            "password_hash" : "settinghashedpassword",
        }
    )

    assert response.status_code == 200
    assert response.json() is not None

    user = user_test_client.test_db.users.find_one({ "_id" : response.json() })
    assert user is not None
    assert user['password_hash'] is not "settinghashedpassword"

def test_create_user_with_username_conflict(populate_existing_username_user):
    user_test_client = populate_existing_username_user
    response = user_test_client.test_client.post(
        '/users/',
        json={
            "username": "test_existing_username",
            "email": "test_existing_user2@testing.com",
            "enabled": True,
            "client_hash" : "abcdefgh123456789"
        }
    )

    assert response.status_code == 409
    assert response.json() == {
            "detail" : "A user with this username already exists."
        }

def test_create_user_with_email_conflict(populate_existing_email_user):
    user_test_client = populate_existing_email_user
    response = user_test_client.test_client.post(
        '/users/',
        json={
            "username": "test_existing_user2",
            "email": "test_existing_email@testing.com",
            "enabled": True,
            "client_hash" : "abcdefgh123456789"
        }
    )

    assert response.status_code == 409
    assert response.json() == {
            "detail" : "A user with this email address already exists."
        }

def test_remove_user(populate_removeable_user):
    user_test_client = populate_removeable_user
    response = user_test_client.test_client.delete('/users/test_delete_user')

    assert response.status_code == 200
    assert response.json() == 1

def test_remove_nonexistent_user(setup):
    user_test_client = setup
    response = user_test_client.test_client.delete('/users/foobar')

    assert response.status_code == 404
    assert response.json() == {
        "detail" : "User not found."
    }
