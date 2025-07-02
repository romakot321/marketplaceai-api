import base64

from src.task.domain.entities import TaskDescribeRun, TaskGenerateRun
from src.integration.domain.schemas import OpenaiRunDescribeRequest, OpenaiRunGenerateRequest


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
        if task_run.file is not None:
            task_run.file.name = "tmp.png"

        return OpenaiRunGenerateRequest(
            image=[task_run.file] if task_run.file is not None else None,
            prompt=self._make_generate_prompt(task_run),
            size=task_run.size,
        )

    def _make_generate_prompt(self, task_run: TaskGenerateRun) -> str:
        if list(task_run.model_dump().values()).count(None) == len(list(task_run.model_dump().values())) - 1 and task_run.background is not None:
            return f"""
                Сгенерируй визуальную карточку товара для маркетплейса. Используй это изображение и следующую информацию:
                • Фон изображения: {task_run.background}
                Требования: – Нужно создать карточку товара, только с изображением товара и фоном, никакой другой информации она содержать не должна.   – Адаптировано под формат маркетплейса (4:5 или 1:1)  – Контрастный, привлекательный, но не перегруженный.
            """

        return f"""
            Сгенерируй визуальную карточку товара для маркетплейса. Используй это изображение и следующую информацию:
            • Название товара: {task_run.title}  • Фон изображения: {task_run.background}  • Офферы или преимущества: {', '.join(task_run.offers)}  • Стиль иконок и элементов: {task_run.icon_style}  • Краткое описание товара: {task_run.description}
            Требования:  – Адаптировано под формат маркетплейса (4:5 или 1:1)  – Контрастный, привлекательный, но не перегруженный.  – Четкая читаемость текста  – Расположение: Название сверху, изображение товара в центре, офферы и стиль иконок — по бокам . - Все слова на карточки товара должны соответствовать содержанию в инфографике  
        """

    _describe_prompt = """Проанализируй изображение и точно определи, что на нём изображено. Назови товар максимально содержательно и конкретно — так, чтобы это было понятно покупателю на маркетплейсе. Название должно быть коротким, не более трёх слов, без лишних описаний. Учитывай форму, материал, тип и назначение предмета.
Затем предложи идеальный фон для карточки товара: он должен подчёркивать продукт, не отвлекать внимание, быть визуально привлекательным и соответствовать стилю/категории товара (например, для техники — нейтральный; для косметики — светлый с мягким градиентом; для кухни — фон в стиле lifestyle и т.д.).
Формат ответа: Название товара: [3 слова максимум] Рекомендованный фон: [Кратко, 1–2 предложения] Затем предложи идеальные офферы для этой карточки товара; офферы должны подчеркивать достоинства продукта, быть понятными и содержательными. Всего нужно перечислить 3 преимущества продукта.  Формат ответа:  Оффер 1: [3 слова максимум] Оффер 2: [3 слова максимум] Оффер 3: [3 слова максимум] Затем предложи идеальный стиль иконок подходящий для этого товара ; иконки товара должены подчеркивать достоинства продукта и быть содержательными. (например, для техники — 3D, объёмные, с мягкими тенями; для кухни - мягкий свет, текстурированно, приятные тени и т.д.). Формат ответа:  Иконка товара: [5 слов максимум] Исходя из своих ответов составь идеальное описание данного товара. Описание должно подчеркивать достоинства и быть коротким и понятным.  Формат ответа: Описание товара: [10 слов максимум] 
Формат json: {"title": Название товара, "background": Рекомендованный фон, "description": Описание товара, "offers": [Оффер 1, Оффер 2, Оффер 3], "icon_style": Иконка товара}"""
