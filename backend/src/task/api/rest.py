from io import BytesIO
from uuid import UUID

from fastapi import File, Depends, APIRouter, UploadFile, BackgroundTasks, Response

from src.core.dependencies import validate_api_token_header
from src.task.api.dependencies import HttpClientDepend, TaskUoWDepend, TaskRunnerDepend, FileStorageDepend
from src.task.application.use_cases.create_task import CreateTaskUseCase
from src.task.application.use_cases.get_task import GetTaskUseCase
from src.task.application.use_cases.get_task_result import GetTaskResultUseCase
from src.task.application.use_cases.run_task_describe import RunTaskDescribeUseCase
from src.task.application.use_cases.run_task_generate import RunTaskGenerateUseCase
from src.task.domain.dtos import TaskReadDTO, TaskDescribeCreateDTO, TaskGenerateCreateDTO

router = APIRouter()


@router.post("/describe", response_model=TaskReadDTO, dependencies=[Depends(validate_api_token_header)])
async def create_and_run_describe_task(
        uow: TaskUoWDepend,
        http_client: HttpClientDepend,
        runner: TaskRunnerDepend,
        background_tasks: BackgroundTasks,
        data: TaskDescribeCreateDTO = Depends(TaskDescribeCreateDTO.as_form),
        file: UploadFile = File(),
):
    task = await CreateTaskUseCase(uow).execute(data)
    file_buffer = BytesIO(await file.read())
    background_tasks.add_task(RunTaskDescribeUseCase(uow, runner, http_client).execute, task.id, data, file_buffer)
    return task


@router.post("/generate", response_model=TaskReadDTO, dependencies=[Depends(validate_api_token_header)])
async def create_and_run_generate_task(
        uow: TaskUoWDepend,
        http_client: HttpClientDepend,
        file_storage: FileStorageDepend,
        runner: TaskRunnerDepend,
        background_tasks: BackgroundTasks,
        file: UploadFile | None = File(None),
        data: TaskGenerateCreateDTO = Depends(TaskGenerateCreateDTO.as_form),
):
    task = await CreateTaskUseCase(uow).execute(data)
    file_buffer = BytesIO(await file.read())
    background_tasks.add_task(RunTaskGenerateUseCase(uow, runner, http_client, file_storage).execute, task.id, data,
                              file_buffer)
    return task


@router.get("/{task_id}", response_model=TaskReadDTO, dependencies=[Depends(validate_api_token_header)])
async def get_task(task_id: UUID, uow: TaskUoWDepend):
    return await GetTaskUseCase(uow).execute(task_id)


@router.get("/{task_id}/result", responses={
    200: {
        "description": "Decoded task result",
        "content": {
            "application/json": {"example": [{}]},
            "image/jpeg": {}
        }
    }
}, dependencies=[Depends(validate_api_token_header)])
async def get_task_result(task_id: UUID, uow: TaskUoWDepend, file_storage: FileStorageDepend):
    result = await GetTaskResultUseCase(uow, file_storage).execute(task_id)
    if isinstance(result, dict):
        return result
    return Response(content=result.read(), media_type="image/jpeg")
