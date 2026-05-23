"""Sınav (Exam) servisi birim testleri."""

from datetime import date, timedelta
from math import ceil

import pytest
from sqlalchemy.orm import Session

from app.domain.enums import LeitnerBox
from app.domain.models import Exam, Flashcard
from app.infrastructure.repositories import ExamRepository, FlashcardRepository
from app.use_cases.exam_service import ExamService


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


def test_create_exam_rejects_today(memory_session: Session) -> None:
    """Bugünkü tarih de reddedilmeli — sınav gelecekte olmalı."""
    service = ExamService(ExamRepository(memory_session), FlashcardRepository(memory_session))

    with pytest.raises(ValueError):
        service.create_exam("Fizik", date.today())


def test_create_exam_rejects_empty_name(memory_session: Session) -> None:
    service = ExamService(ExamRepository(memory_session), FlashcardRepository(memory_session))

    with pytest.raises(ValueError):
        service.create_exam("   ", date.today() + timedelta(days=5))


def test_build_study_session_with_no_remaining_days(memory_session: Session) -> None:
    exam = Exam.create("Kimya", date.today())
    memory_session.add(exam)
    memory_session.commit()

    service = ExamService(ExamRepository(memory_session), FlashcardRepository(memory_session))
    study_session = service.build_study_session(exam, [], completed_today=0)

    assert study_session.remaining_days == 0
    assert study_session.daily_target == 0


def test_build_study_session_excludes_mastered(memory_session: Session) -> None:
    """Mastered kartlar günlük hedeften hariç tutulmalı."""
    exam = Exam.create("Biyoloji", date.today() + timedelta(days=5))
    memory_session.add(exam)
    memory_session.commit()

    cards = []
    for i in range(6):
        c = Flashcard.create(exam_id=exam.ExamId, front_side=f"Soru {i}", back_side=f"Cevap {i}")
        memory_session.add(c)
        cards.append(c)
    memory_session.commit()

    # 2 kartı Mastered yap
    cards[0].Status = LeitnerBox.Mastered
    cards[1].Status = LeitnerBox.Mastered
    memory_session.commit()

    service = ExamService(ExamRepository(memory_session), FlashcardRepository(memory_session))
    session = service.build_study_session(exam, cards, completed_today=0)

    # 4 aktif kart / 5 gün = ceil(0.8) = 1
    assert session.daily_target == ceil(4 / 5)


def test_build_study_session_ceiling_division(memory_session: Session) -> None:
    """5 aktif kart / 3 gün = ceil(1.67) = 2 olmalı (floor değil)."""
    exam = Exam.create("Matematik", date.today() + timedelta(days=3))
    memory_session.add(exam)
    memory_session.commit()

    cards = []
    for i in range(5):
        c = Flashcard.create(exam_id=exam.ExamId, front_side=f"S{i}", back_side=f"C{i}")
        memory_session.add(c)
        cards.append(c)
    memory_session.commit()

    service = ExamService(ExamRepository(memory_session), FlashcardRepository(memory_session))
    session = service.build_study_session(exam, cards, completed_today=0)

    assert session.daily_target == 2  # ceil(5/3)


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
