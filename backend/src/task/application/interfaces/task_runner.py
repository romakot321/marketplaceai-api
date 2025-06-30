import abc
from typing import Generic, TypeVar

from src.task.domain.entities import TaskDescribeRun, TaskGenerateRun

TResponseData = TypeVar("TResponseData")


class ITaskRunner(abc.ABC, Generic[TResponseData]):
    @abc.abstractmethod
    async def start_describe(self, data: TaskDescribeRun) -> TResponseData: ...

    @abc.abstractmethod
    async def start_generate(self, data: TaskGenerateRun) -> TResponseData: ...

    @abc.abstractmethod
    async def get_result(self, external_task_id: str) -> TResponseData | None: ...
