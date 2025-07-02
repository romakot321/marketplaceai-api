from io import BytesIO
from typing import Type
from httpx import AsyncClient
from pydantic import BaseModel
import pytest

from src.core.config import settings
from src.task.domain.dtos import TaskDescribeCreateDTO, TaskGenerateCreateDTO


def _fill_dto(dto: Type[BaseModel]) -> dict:
    data = {}
    for name, field in dto.model_fields.items():
        if field.annotation is str:
            data[name] = "string"
        elif field.annotation is list:
            data[name] = []
        elif field.annotation is int:
            data[name] = 0
        elif isinstance(field.annotation, BaseModel):
            data[name] = _fill_dto(data[name])
        else:
            data[name] = None
    return data


@pytest.mark.asyncio(loop_scope="session")
async def test_task_describe_create(test_client: AsyncClient):
    data = _fill_dto(TaskDescribeCreateDTO)
    data.pop("webhook_url")
    file = BytesIO(b"123")
    file.name = "file.png"

    resp = await test_client.post("/api/task/describe", data=data, files={"file": file}, headers={"Api-Token": settings.API_TOKEN})
    assert resp.status_code == 200, resp.json()


@pytest.mark.asyncio(loop_scope="session")
async def test_task_describe_create(test_client: AsyncClient):
    data = _fill_dto(TaskDescribeCreateDTO)
    data.pop("webhook_url")
    file = BytesIO(b"123")
    file.name = "file.png"

    resp = await test_client.post("/api/task/describe", data=data, files={"file": file}, headers={"Api-Token": settings.API_TOKEN})
    assert resp.status_code == 200, resp.json()


@pytest.mark.asyncio(loop_scope="session")
async def test_task_generate_create(test_client: AsyncClient):
    data = _fill_dto(TaskGenerateCreateDTO)
    data.pop("webhook_url")
    data["size"] = "auto"
    file = BytesIO(b"123")
    file.name = "file.png"

    resp = await test_client.post("/api/task/generate", data=data, files={"file": file}, headers={"Api-Token": settings.API_TOKEN})
    assert resp.status_code == 200, resp.json()


@pytest.mark.asyncio(loop_scope="session")
async def test_task_describe_get_result(test_client: AsyncClient):
    data = _fill_dto(TaskDescribeCreateDTO)
    data.pop("webhook_url")
    data["size"] = "auto"
    file = BytesIO(b"123")
    file.name = "file.png"

    resp = await test_client.post("/api/task/describe", data=data, files={"file": file}, headers={"Api-Token": settings.API_TOKEN})
    assert resp.status_code == 200, resp.json()
    task_id = resp.json()["id"]

    resp = await test_client.get(f"/api/task/{task_id}/result")
    assert resp.status_code == 200, resp.json()
    assert resp.json() == dict(description="a", background="b", title="c", offers=["d"], icon_style="e")


@pytest.mark.asyncio(loop_scope="session")
async def test_task_describe_get_result(test_client: AsyncClient):
    data = _fill_dto(TaskDescribeCreateDTO)
    data.pop("webhook_url")
    data["size"] = "auto"
    file = BytesIO(b"123")
    file.name = "file.png"

    resp = await test_client.post("/api/task/describe", data=data, files={"file": file}, headers={"Api-Token": settings.API_TOKEN})
    assert resp.status_code == 200, resp.json()
    task_id = resp.json()["id"]

    resp = await test_client.get(f"/api/task/{task_id}/result", headers={"Api-Token": settings.API_TOKEN})
    assert resp.status_code == 200, resp.json()
    assert resp.json() == dict(description="a", background="b", title="c", offers=["d"], icon_style="e")


@pytest.mark.asyncio(loop_scope="session")
async def test_task_generate_get_result(test_client: AsyncClient):
    data = _fill_dto(TaskGenerateCreateDTO)
    data.pop("webhook_url")
    data["size"] = "auto"
    file = BytesIO(b"123")
    file.name = "file.png"

    resp = await test_client.post("/api/task/generate", data=data, files={"file": file}, headers={"Api-Token": settings.API_TOKEN})
    assert resp.status_code == 200, resp.json()
    task_id = resp.json()["id"]

    resp = await test_client.get(f"/api/task/{task_id}/result", headers={"Api-Token": settings.API_TOKEN})
    assert resp.status_code == 200, resp.json()
    assert resp.headers["Content-Type"] == "image/jpeg"
    assert resp.read() == b"123"

