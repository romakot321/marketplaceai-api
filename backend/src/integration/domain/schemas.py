from io import BytesIO
from typing import Literal

from pydantic import BaseModel, ConfigDict


class OpenaiRunDescribeRequest(BaseModel):
    class GPTInput(BaseModel):
        class GptInputContent(BaseModel):
            type: Literal["input_text", "input_image"]
            text: str | None = None
            image_url: str | None = None

        role: str
        content: list[GptInputContent]

    model: str = "gpt-4.1"
    input: list[GPTInput]

    model_config = ConfigDict(arbitrary_types_allowed=True)


class OpenaiRunDescribeResponse(BaseModel):
    description: str
    background: str
    title: str
    offers: list[str]
    icon_style: str


class OpenaiRunGenerateRequest(BaseModel):
    model: str = "gpt-image-1"
    image: list[BytesIO] | None = None
    prompt: str
    n: int = 1
    output_format: str = "jpeg"
    size: Literal["1024x1024", "1536x1024", "1024x1536", "auto"]

    model_config = ConfigDict(arbitrary_types_allowed=True)


class OpenaiRunGenerateResponse(BaseModel):
    image: BytesIO

    model_config = ConfigDict(arbitrary_types_allowed=True)
