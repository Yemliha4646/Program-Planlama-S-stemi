import os
from collections.abc import Generator

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./program_planlama.db")
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    future=True,
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


class Base(DeclarativeBase):
    """SQLAlchemy 2.0 uyumlu bildirimsel taban sınıfı."""
    pass


def get_db() -> Generator[Session, None, None]:
    """Bağımlılık enjeksiyonu için veritabanı oturumu üretir."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
