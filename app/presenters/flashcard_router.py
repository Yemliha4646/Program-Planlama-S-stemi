"""Flashcard API endpoint'leri — kart oluşturma, Leitner güncellemesi ve silme."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.config import get_db
from app.infrastructure.repositories import ExamRepository, FlashcardRepository
from app.presenters.schemas import FlashcardCreateSchema, FlashcardResponseSchema, LeitnerUpdateSchema
from app.use_cases.flashcard_service import FlashcardService

router = APIRouter(prefix="/api/flashcards", tags=["flashcards"])


@router.post("/", response_model=FlashcardResponseSchema, status_code=201)
def create_flashcard(flashcard_payload: FlashcardCreateSchema, db: Session = Depends(get_db)) -> FlashcardResponseSchema:
    """Yeni bir flashcard oluşturur ve ilişkili sınava bağlar."""
    exam_repository = ExamRepository(db)
    flashcard_repository = FlashcardRepository(db)
    flashcard_service = FlashcardService(flashcard_repository)
    exam = exam_repository.get(flashcard_payload.exam_id)
    if exam is None:
        raise HTTPException(status_code=404, detail="Belirtilen sınav bulunamadı. Flashcard eklenemiyor.")

    try:
        flashcard = flashcard_service.create_flashcard(
            exam,
            flashcard_payload.front_side,
            flashcard_payload.back_side,
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    return FlashcardResponseSchema(
        card_id=flashcard.CardId,
        exam_id=flashcard.ExamId,
        front_side=flashcard.FrontSide,
        back_side=flashcard.BackSide,
        status=flashcard.Status,
    )


@router.patch("/{card_id}/leitner", response_model=FlashcardResponseSchema)
def update_flashcard_leitner(card_id: str, status_payload: LeitnerUpdateSchema, db: Session = Depends(get_db)) -> FlashcardResponseSchema:
    """Flashcard'ın Leitner kutusunu günceller (Bildim/Bilemedim)."""
    flashcard_repository = FlashcardRepository(db)
    flashcard_service = FlashcardService(flashcard_repository)
    flashcard = flashcard_repository.get(card_id)
    if flashcard is None:
        raise HTTPException(status_code=404, detail="Belirtilen flashcard bulunamadı.")

    try:
        updated = flashcard_service.update_leitner(flashcard, status_payload.known)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    return FlashcardResponseSchema(
        card_id=updated.CardId,
        exam_id=updated.ExamId,
        front_side=updated.FrontSide,
        back_side=updated.BackSide,
        status=updated.Status,
    )


@router.delete("/{card_id}", status_code=204)
def delete_flashcard(card_id: str, db: Session = Depends(get_db)) -> None:
    """Flashcard'ı kalıcı olarak siler."""
    flashcard_repository = FlashcardRepository(db)
    flashcard = flashcard_repository.get(card_id)
    if flashcard is None:
        raise HTTPException(status_code=404, detail="Belirtilen flashcard bulunamadı.")
    flashcard_repository.delete(flashcard)
