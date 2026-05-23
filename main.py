"""Program Planlama Sistemi — FastAPI uygulama giriş noktası."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from app.infrastructure.database import init_db
from app.presenters.exam_router import router as exam_router
from app.presenters.flashcard_router import router as flashcard_router

# Loglama konfigürasyonu
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(application: FastAPI):
    """Uygulama yaşam döngüsü: başlangıçta veritabanını oluşturur."""
    init_db()
    logger.info("Veritabanı başarıyla başlatıldı.")
    yield


app = FastAPI(
    title="Program Planlama Sistemi",
    description="FastAPI tabanlı sınav planlama ve Leitner flashcard uygulaması.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — farklı origin'lerden erişime izin ver
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(exam_router)
app.include_router(flashcard_router)
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", include_in_schema=False)
def root() -> RedirectResponse:
    """Kök URL'yi frontend arayüzüne yönlendirir."""
    return RedirectResponse(url="/static/index.html")
