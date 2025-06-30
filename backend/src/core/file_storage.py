from io import BytesIO
from pathlib import Path


class FileStorage:
    directory = Path("storage")

    @classmethod
    def write(cls, filename: str, file_body: BytesIO):
        with open(cls.directory / filename, "wb") as f:
            for chunk in file_body:
                f.write(chunk)

    @classmethod
    def read(cls, filename: str) -> BytesIO:
        buffer = BytesIO()
        with open(cls.directory / filename, "rb") as f:
            buffer.write(f.read())
        buffer.seek(0)
        return buffer
