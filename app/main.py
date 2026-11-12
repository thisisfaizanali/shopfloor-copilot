from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import FastAPI
from pydantic import BaseModel, StringConstraints

from app import rag


@asynccontextmanager
async def lifespan(_):
    rag.build_index()
    yield


app = FastAPI(lifespan=lifespan)


class Ask(BaseModel):
    question: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=500)]


@app.post("/api/ask")
def ask(body: Ask):
    return rag.answer(body.question)
