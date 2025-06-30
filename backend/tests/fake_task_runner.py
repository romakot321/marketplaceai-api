from io import BytesIO

from src.integration.domain.dtos import IntegrationTaskResultDTO, IntegrationTaskStatus
from src.integration.domain.schemas import OpenaiRunDescribeResponse
from src.task.application.interfaces.task_runner import ITaskRunner, TResponseData
from src.task.domain.entities import TaskGenerateRun, TaskDescribeRun


class FakeTaskRunner(ITaskRunner):
    def __init__(self):
        self.tasks = []

    async def start_describe(self, data: TaskDescribeRun) -> IntegrationTaskResultDTO:
        self.tasks.append(data)
        return IntegrationTaskResultDTO(status=IntegrationTaskStatus.started, external_task_id=str(len(self.tasks) - 1))

    async def start_generate(self, data: TaskGenerateRun) -> IntegrationTaskResultDTO:
        self.tasks.append(data)
        return IntegrationTaskResultDTO(status=IntegrationTaskStatus.started, external_task_id=str(len(self.tasks) - 1))

    async def get_result(self, external_task_id: str) -> IntegrationTaskResultDTO | None:
        task = self.tasks[int(external_task_id)]
        if isinstance(task, TaskDescribeRun):
            result = OpenaiRunDescribeResponse(description="a", background="b", title="c", offers=["d"], icon_style="e").model_dump_json()
        else:
            result = BytesIO(b"123")
        return IntegrationTaskResultDTO(status=IntegrationTaskStatus.finished, external_task_id=external_task_id, result=result)
