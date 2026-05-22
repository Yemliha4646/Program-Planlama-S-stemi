from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from app.infrastructure.database import init_db
from app.presenters.exam_router import router as exam_router
from app.presenters.flashcard_router import router as flashcard_router

app = FastAPI(
    title="Program Planlama Sistemi",
    description="FastAPI tabanlı sınav planlama ve Leitner flashcard uygulaması.",
)

app.include_router(exam_router)
app.include_router(flashcard_router)
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.on_event("startup")
def startup_event() -> None:
    init_db()


@app.get("/", include_in_schema=False)
def root() -> RedirectResponse:
    return RedirectResponse(url="/static/index.html")
