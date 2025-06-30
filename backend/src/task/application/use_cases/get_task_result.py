import json
from io import BytesIO
from uuid import UUID

from fastapi import HTTPException

from src.core.file_storage import FileStorage
from src.db.exceptions import DBModelNotFoundException
from src.task.application.interfaces.task_uow import ITaskUnitOfWork


class GetTaskResultUseCase:
    def __init__(self, uow: ITaskUnitOfWork, file_storage: FileStorage):
        self.uow = uow
        self.file_storage = file_storage

    async def execute(self, task_id: UUID) -> dict | BytesIO:
        async with self.uow:
            try:
                task = await self.uow.tasks.get_by_pk(task_id)
            except DBModelNotFoundException:
                raise HTTPException(404)

        if task.result is None:
            raise HTTPException(400, detail="Task doesn't has result")
        if task.result.startswith("https://"):
            return self.file_storage.read(str(task_id))

        return json.loads(task.result)
