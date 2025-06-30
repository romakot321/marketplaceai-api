import base64

from src.integration.domain.schemas import OpenaiRunDescribeRequest, OpenaiRunGenerateRequest
from src.task.domain.entities import TaskDescribeRun, TaskGenerateRun


class TaskRunToRequestMapper:
    def map_describe(self, task_run: TaskDescribeRun) -> OpenaiRunDescribeRequest:
        base64_image = base64.b64encode(task_run.file.read()).decode()

        return OpenaiRunDescribeRequest(
            input=[
                OpenaiRunDescribeRequest.GPTInput(
                    role="user",
                    content=[
                        OpenaiRunDescribeRequest.GPTInput.GptInputContent(
                            type="input_text",
                            text=self._describe_prompt,
                        ),
                        OpenaiRunDescribeRequest.GPTInput.GptInputContent(
                            type="input_image",
                            image_url=f"data:image/jpeg;base64,{base64_image}"
                        )
                    ]
                )
            ]
        )

    def map_generate(self, task_run: TaskGenerateRun) -> OpenaiRunGenerateRequest:
        return OpenaiRunGenerateRequest(
            image=[task_run.file] if task_run.file is not None else None,
            prompt=self._make_generate_prompt(task_run),
            size=task_run.size,
        )

    def _make_generate_prompt(self, task_run: TaskGenerateRun) -> str:
        return task_run.title

    _describe_prompt = ""
