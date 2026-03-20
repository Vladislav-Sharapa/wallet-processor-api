from contextlib import asynccontextmanager
from io import BytesIO
from typing import AsyncGenerator


@asynccontextmanager
async def file_buffer_generator() -> AsyncGenerator[BytesIO, None]:
    buffer = BytesIO()
    try:
        yield buffer
    finally:
        buffer.close()
