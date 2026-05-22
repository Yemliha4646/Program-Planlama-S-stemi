from app.core.config import Base, engine


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
