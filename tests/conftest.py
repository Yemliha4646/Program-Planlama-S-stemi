"""Ortak test fixture'ları — tüm test dosyaları tarafından paylaşılır."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import Base, get_db
from main import app


@pytest.fixture(name="memory_engine")
def fixture_memory_engine():
    """SQLite in-memory engine — StaticPool ile tüm thread'ler aynı bağlantıyı paylaşır."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    engine.dispose()


@pytest.fixture(name="memory_session")
def fixture_memory_session(memory_engine) -> Session:
    """In-memory veritabanı oturumu — birim testleri için."""
    TestingSessionLocal = sessionmaker(
        bind=memory_engine, autoflush=False, autocommit=False, future=True
    )
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(name="client")
def fixture_test_client(memory_engine):
    """FastAPI TestClient — in-memory DB kullanarak API testleri yapar."""
    TestingSessionLocal = sessionmaker(
        bind=memory_engine, autoflush=False, autocommit=False, future=True
    )

    def override_get_db():
        session = TestingSessionLocal()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
