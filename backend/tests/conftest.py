from typing import AsyncGenerator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from src.main import app
from src.task.api.dependencies import get_task_runner
from tests.fake_task_runner import FakeTaskRunner


@pytest_asyncio.fixture(scope="session")
async def test_client() -> AsyncGenerator[AsyncClient, None]:
    app.dependency_overrides[get_task_runner] = lambda: FakeTaskRunner()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client
