"""Ortak test fixture'ları — tüm test dosyaları tarafından paylaşılır."""

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session

from app.core.config import Base


@pytest.fixture(name="memory_session")
def fixture_memory_session() -> Session:
    """SQLite in-memory veritabanı ile test oturumu oluşturur.
    Foreign key constraint'leri etkinleştirilir."""
    engine = create_engine("sqlite:///:memory:", future=True)

    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(bind=engine)
    session = Session(bind=engine, future=True)
    try:
        yield session
    finally:
        session.close()
