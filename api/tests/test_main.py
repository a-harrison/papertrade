import pytest
from httpx import AsyncClient
from ..main import app

@pytest.fixture()
async def setup_async_client(scope="session"):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.mark.asyncio
async def test_read_main(setup_async_client):
    ac = setup_async_client
    response = await ac.get("/")
    assert response.status_code == 200
    assert response.json() == {"message" : "Hello World"}
