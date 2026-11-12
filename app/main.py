from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from google.genai import errors
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
    try:
        return rag.answer(body.question)
    except errors.APIError:  # rate limit (429), overloaded (503), timeout (504)
        return JSONResponse(
            status_code=503,
            content={"detail": "The AI service is busy or unavailable. Please try again in a minute."},
        )
