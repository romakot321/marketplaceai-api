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
        return f"{task_run.model_dump()}. Сделай из этого изображения карточку товара для маркетплейса. Используй данные которые получил ранее. Улучши качество изображения предмета. Не меняй содержание данных полученных ранее."

    _describe_prompt = """ПРОМТ 1 Проанализируй изображение и точно определи, что на нём изображено. Назови товар максимально содержательно и конкретно — так, чтобы это было понятно покупателю на маркетплейсе. Название должно быть коротким, не более трёх слов, без лишних описаний. Учитывай форму, материал, тип и назначение предмета.
Затем предложи идеальный фон для карточки товара: он должен подчёркивать продукт, не отвлекать внимание, быть визуально привлекательным и соответствовать стилю/категории товара (например, для техники — нейтральный; для косметики — светлый с мягким градиентом; для кухни — фон в стиле lifestyle и т.д.).
Формат ответа: {"title": [3 слова максимум], "background": [Кратко, 1–2 предложения], "description": "", "offers": ["offer1", "offer2", "offer3"], "icon_style": ""}"""
