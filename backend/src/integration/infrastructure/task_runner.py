import uuid
import base64
import asyncio
from io import BytesIO

from openai import AsyncOpenAI, OpenAIError
from pydantic import ValidationError

from src.core.config import settings
from src.task.domain.entities import TaskDescribeRun, TaskGenerateRun
from src.integration.domain.dtos import IntegrationTaskStatus, IntegrationTaskResultDTO
from src.integration.domain.mappers import TaskRunToRequestMapper
from src.integration.domain.schemas import OpenaiRunDescribeRequest, OpenaiRunGenerateRequest, OpenaiRunDescribeResponse
from src.integration.domain.exceptions import IntegrationRequestException
from src.task.application.interfaces.task_runner import ITaskRunner

tasks = {}


class OpenaiTaskRunner(ITaskRunner[IntegrationTaskResultDTO]):
    token: str = settings.OPENAI_API_TOKEN

    def __init__(self) -> None:
        global tasks
        self.client = AsyncOpenAI()
        self.tasks = tasks

    def _create_task(self) -> str:
        id = str(uuid.uuid4())
        self.tasks[id] = {"status": IntegrationTaskStatus.started}
        return id

    def _set_task_result(self, task_id: str, status: IntegrationTaskStatus, result: BytesIO | str):
        self.tasks[task_id] = {"result": result, "status": status}

    async def _image2text(self, task_id: str, request: OpenaiRunDescribeRequest):
        try:
            result = await self.client.responses.create(**request.model_dump(exclude_none=True))
        except OpenAIError as e:
            self._set_task_result(task_id, IntegrationTaskStatus.failed, str(e))
            return

        try:
            OpenaiRunDescribeResponse.model_validate_json(result.output_text)
        except ValidationError as e:
            self._set_task_result(task_id, IntegrationTaskStatus.failed, "Unexpected openai response: " + str(e))
            return

        self._set_task_result(task_id, IntegrationTaskStatus.finished, result.output_text)

    async def start_describe(self, data: TaskDescribeRun) -> IntegrationTaskResultDTO:
        external_task_id = self._create_task()
        request = TaskRunToRequestMapper().map_describe(data)
        asyncio.create_task(self._image2text(external_task_id, request))
        return IntegrationTaskResultDTO(status=IntegrationTaskStatus.queued, external_task_id=external_task_id)

    async def _image2image(self, task_id: str, request: OpenaiRunGenerateRequest):
        try:
            result = await self.client.images.edit(**request.model_dump(exclude_none=True))
        except OpenAIError as e:
            self._set_task_result(task_id, IntegrationTaskStatus.failed, str(e))
            return

        image = BytesIO(base64.b64decode(result.data[0].b64_json))
        self._set_task_result(task_id, IntegrationTaskStatus.finished, image)

    async def _text2image(self, task_id: str, request: OpenaiRunGenerateRequest):
        try:
            result = await self.client.images.generate(**request.model_dump(exclude_none=True))
        except OpenAIError as e:
            self._set_task_result(task_id, IntegrationTaskStatus.failed, str(e))
            return

        image = BytesIO(base64.b64decode(result.data[0].b64_json))
        self._set_task_result(task_id, IntegrationTaskStatus.finished, image)

    async def start_generate(self, data: TaskGenerateRun) -> IntegrationTaskResultDTO:
        external_task_id = self._create_task()
        request = TaskRunToRequestMapper().map_generate(data)

        if data.file is not None:
            asyncio.create_task(self._image2image(external_task_id, request))
        else:
            asyncio.create_task(self._text2image(external_task_id, request))

        return IntegrationTaskResultDTO(status=IntegrationTaskStatus.queued, external_task_id=external_task_id)

    async def get_result(self, external_task_id: str) -> IntegrationTaskResultDTO | None:
        task = self.tasks.get(external_task_id)
        if task is None:
            raise IntegrationRequestException("Task not found")

        return IntegrationTaskResultDTO(
            status=task.get("status", IntegrationTaskStatus.started),
            external_task_id=external_task_id,
            result=task.get("result"),
            error=task.get("result") if task.get("status") == IntegrationTaskStatus.failed else None,
        )
