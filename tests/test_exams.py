from datetime import date, timedelta

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.core.config import Base
from app.domain.models import Exam, Flashcard
from app.infrastructure.repositories import ExamRepository, FlashcardRepository
from app.use_cases.exam_service import ExamService


@pytest.fixture(name="memory_session")
def fixture_memory_session() -> Session:
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(bind=engine)
    session = Session(bind=engine, future=True)
    try:
        yield session
    finally:
        session.close()


def test_create_exam_with_future_date(memory_session: Session) -> None:
    service = ExamService(ExamRepository(memory_session), FlashcardRepository(memory_session))
    exam = service.create_exam("Veri Tabanı Yönetim Sistemleri", date.today() + timedelta(days=10))

    assert exam.CourseName == "Veri Tabanı Yönetim Sistemleri"
    assert exam.ExamDate > date.today()
    assert len(exam.ExamId) == 36


def test_create_exam_rejects_past_date(memory_session: Session) -> None:
    service = ExamService(ExamRepository(memory_session), FlashcardRepository(memory_session))

    with pytest.raises(ValueError):
        service.create_exam("Matematik", date.today() - timedelta(days=1))


def test_build_study_session_with_no_remaining_days(memory_session: Session) -> None:
    exam = Exam.create("Kimya", date.today())
    memory_session.add(exam)
    memory_session.commit()

    service = ExamService(ExamRepository(memory_session), FlashcardRepository(memory_session))
    study_session = service.build_study_session(exam, [], completed_today=0)

    assert study_session.remaining_days == 0
    assert study_session.daily_target == 0


def test_delete_exam_cascade_deletes_flashcards(memory_session: Session) -> None:
    exam = Exam.create("Fizik", date.today() + timedelta(days=7))
    memory_session.add(exam)
    memory_session.commit()

    flashcard = Flashcard.create(
        exam_id=exam.ExamId,
        front_side="Hareket nedir?",
        back_side="Cisimlerin yer değiştirmesidir.",
    )
    memory_session.add(flashcard)
    memory_session.commit()

    service = ExamService(ExamRepository(memory_session), FlashcardRepository(memory_session))
    loaded_exam = service.get_exam(exam.ExamId)
    assert loaded_exam is not None

    service.delete_exam(loaded_exam)

    remaining_cards = memory_session.query(Flashcard).all()
    assert remaining_cards == []
