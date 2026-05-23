from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from app.infrastructure.database import init_db
from app.presenters.exam_router import router as exam_router
from app.presenters.flashcard_router import router as flashcard_router


@asynccontextmanager
async def lifespan(application: FastAPI):
    """Uygulama yaşam döngüsü: başlangıçta veritabanını oluşturur."""
    init_db()
    yield


app = FastAPI(
    title="Program Planlama Sistemi",
    description="FastAPI tabanlı sınav planlama ve Leitner flashcard uygulaması.",
    lifespan=lifespan,
)

app.include_router(exam_router)
app.include_router(flashcard_router)
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", include_in_schema=False)
def root() -> RedirectResponse:
    return RedirectResponse(url="/static/index.html")
