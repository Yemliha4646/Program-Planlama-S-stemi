"""Flashcard servisi birim testleri."""

from datetime import date, timedelta

import pytest
from sqlalchemy.orm import Session

from app.domain.enums import LeitnerBox
from app.domain.models import Exam, Flashcard
from app.infrastructure.repositories import FlashcardRepository
from app.use_cases.flashcard_service import FlashcardService


def test_create_flashcard_and_read_data(memory_session: Session) -> None:
    exam = Exam.create("Biyoloji", date.today() + timedelta(days=5))
    memory_session.add(exam)
    memory_session.commit()

    repository = FlashcardRepository(memory_session)
    service = FlashcardService(repository)

    flashcard = service.create_flashcard(exam, "DNA nedir?", "Genetik bilgiyi taşıyan moleküldür.")

    assert flashcard.ExamId == exam.ExamId
    assert flashcard.FrontSide == "DNA nedir?"
    assert flashcard.BackSide == "Genetik bilgiyi taşıyan moleküldür."
    assert flashcard.Status.name == "Box1"


def test_promote_flashcard_through_leitner(memory_session: Session) -> None:
    exam = Exam.create("Felsefe", date.today() + timedelta(days=8))
    memory_session.add(exam)
    memory_session.commit()

    repository = FlashcardRepository(memory_session)
    service = FlashcardService(repository)
    flashcard = service.create_flashcard(exam, "Ahlak nedir?", "İyi ve kötü arasındaki kurallardır.")

    promoted_box2 = service.update_leitner(flashcard, True)
    assert promoted_box2.Status.name == "Box2"

    promoted_box3 = service.update_leitner(promoted_box2, True)
    assert promoted_box3.Status.name == "Box3"

    promoted_mastered = service.update_leitner(promoted_box3, True)
    assert promoted_mastered.Status.name == "Mastered"


def test_mastered_card_stays_mastered_on_known(memory_session: Session) -> None:
    """Mastered kartlara 'Bildim' basılınca seviye değişmemeli — zaten en üst."""
    exam = Exam.create("Kimya", date.today() + timedelta(days=3))
    memory_session.add(exam)
    memory_session.commit()

    repository = FlashcardRepository(memory_session)
    service = FlashcardService(repository)
    flashcard = service.create_flashcard(exam, "H2O nedir?", "Su molekülüdür.")

    # Mastered'a kadar yükselt
    flashcard = service.update_leitner(flashcard, True)   # Box1 → Box2
    flashcard = service.update_leitner(flashcard, True)   # Box2 → Box3
    flashcard = service.update_leitner(flashcard, True)   # Box3 → Mastered

    # Mastered'da iken "Bildim" bas — Mastered kalmalı
    result = service.update_leitner(flashcard, True)
    assert result.Status.name == "Mastered"


def test_reset_flashcard_to_box1_when_bilemedim(memory_session: Session) -> None:
    exam = Exam.create("Tarih", date.today() + timedelta(days=12))
    memory_session.add(exam)
    memory_session.commit()

    repository = FlashcardRepository(memory_session)
    service = FlashcardService(repository)
    flashcard = service.create_flashcard(exam, "Tarihte ilk uygarlık?", "Mezopotamya uygarlığıdır.")

    flashcard = service.update_leitner(flashcard, True)  # Box1 → Box2
    assert flashcard.Status.name == "Box2"

    reset_card = service.update_leitner(flashcard, False)
    assert reset_card.Status.name == "Box1"


def test_create_flashcard_rejects_empty_front(memory_session: Session) -> None:
    exam = Exam.create("Edebiyat", date.today() + timedelta(days=5))
    memory_session.add(exam)
    memory_session.commit()

    repository = FlashcardRepository(memory_session)
    service = FlashcardService(repository)

    with pytest.raises(ValueError):
        service.create_flashcard(exam, "   ", "Bir cevap")


def test_create_flashcard_rejects_empty_back(memory_session: Session) -> None:
    exam = Exam.create("Coğrafya", date.today() + timedelta(days=5))
    memory_session.add(exam)
    memory_session.commit()

    repository = FlashcardRepository(memory_session)
    service = FlashcardService(repository)

    with pytest.raises(ValueError):
        service.create_flashcard(exam, "Bir soru", "  ")
