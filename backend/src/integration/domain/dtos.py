from io import BytesIO
from enum import Enum
from typing import Literal

from pydantic import BaseModel, ConfigDict


class IntegrationTaskStatus(str, Enum):
    queued = "queued"
    started = "started"
    finished = "finished"
    failed = "failed"


class IntegrationTaskDescribeRunParamsDTO(BaseModel):
    pass


class IntegrationTaskGenerateRunParamsDTO(BaseModel):
    size: Literal["1024x1024", "1536x1024", "1024x1536", "auto"]
    description: str | None = None
    background: str
    title: str | None = None
    offers: list[str] | None = None
    icon_style: str | None = None


class IntegrationTaskResultDTO(BaseModel):
    status: IntegrationTaskStatus
    external_task_id: str | None = None
    result: str | BytesIO | None = None
    error: str | None = None

    model_config = ConfigDict(arbitrary_types_allowed=True)
