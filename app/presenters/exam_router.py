from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.config import get_db
from app.infrastructure.repositories import ExamRepository, FlashcardRepository
from app.presenters.schemas import (
    ExamCreateSchema,
    ExamResponseSchema,
    ExamUpdateSchema,
    FlashcardResponseSchema,
)
from app.use_cases.exam_service import ExamService
from app.services.ai_service import generate_flashcards_raw

router = APIRouter(prefix="/api/exams", tags=["exams"])


def build_exam_response(exam, session, flashcards):
    from app.domain.enums import LeitnerBox
    mastered = sum(1 for c in flashcards if c.Status == LeitnerBox.Mastered)
    return ExamResponseSchema(
        exam_id=exam.ExamId,
        course_name=exam.CourseName,
        exam_date=exam.ExamDate,
        remaining_days=session.remaining_days,
        daily_target=session.daily_target,
        flashcard_count=len(flashcards),
        mastered_count=mastered,
    )


@router.post("/", response_model=ExamResponseSchema, status_code=201)
def create_exam(exam_payload: ExamCreateSchema, db: Session = Depends(get_db)) -> ExamResponseSchema:
    exam_service = ExamService(ExamRepository(db), FlashcardRepository(db))
    exam = exam_service.create_exam(exam_payload.course_name, exam_payload.exam_date)
    session = exam_service.build_study_session(exam, [], completed_today=0)
    return build_exam_response(exam, session, [])


@router.get("/", response_model=list[ExamResponseSchema])
def list_exams(db: Session = Depends(get_db)) -> list[ExamResponseSchema]:
    exam_repository = ExamRepository(db)
    flashcard_repository = FlashcardRepository(db)
    exam_service = ExamService(exam_repository, flashcard_repository)
    exams = exam_repository.list()
    responses: list[ExamResponseSchema] = []
    for exam in exams:
        flashcards = flashcard_repository.list_by_exam(exam.ExamId)
        session = exam_service.build_study_session(exam, flashcards, completed_today=0)
        responses.append(build_exam_response(exam, session, flashcards))
    return responses


@router.get("/{exam_id}", response_model=ExamResponseSchema)
def get_exam(exam_id: str, db: Session = Depends(get_db)) -> ExamResponseSchema:
    exam_repository = ExamRepository(db)
    flashcard_repository = FlashcardRepository(db)
    exam_service = ExamService(exam_repository, flashcard_repository)
    exam = exam_repository.get(exam_id)
    if exam is None:
        raise HTTPException(status_code=404, detail="Exam bulunamadı.")
    flashcards = flashcard_repository.list_by_exam(exam.ExamId)
    session = exam_service.build_study_session(exam, flashcards, completed_today=0)
    return build_exam_response(exam, session, flashcards)


@router.patch("/{exam_id}", response_model=ExamResponseSchema)
def update_exam(exam_id: str, update_payload: ExamUpdateSchema, db: Session = Depends(get_db)) -> ExamResponseSchema:
    exam_repository = ExamRepository(db)
    flashcard_repository = FlashcardRepository(db)
    exam_service = ExamService(exam_repository, flashcard_repository)
    exam = exam_repository.get(exam_id)
    if exam is None:
        raise HTTPException(status_code=404, detail="Exam bulunamadı.")
    updated = exam_service.update_exam_date(exam, update_payload.exam_date)
    flashcards = flashcard_repository.list_by_exam(updated.ExamId)
    session = exam_service.build_study_session(updated, flashcards, completed_today=0)
    return build_exam_response(updated, session, flashcards)


@router.delete("/{exam_id}")
def delete_exam(exam_id: str, db: Session = Depends(get_db)) -> dict[str, str]:
    exam_repository = ExamRepository(db)
    exam = exam_repository.get(exam_id)
    if exam is None:
        raise HTTPException(status_code=404, detail="Exam bulunamadı.")
    exam_repository.delete(exam)
    return {"message": "Exam ve bağlı flashcardlar silindi."}


@router.get("/{exam_id}/flashcards", response_model=list[FlashcardResponseSchema])
def list_exam_flashcards(exam_id: str, db: Session = Depends(get_db)) -> list[FlashcardResponseSchema]:
    exam_repository = ExamRepository(db)
    flashcard_repository = FlashcardRepository(db)
    exam = exam_repository.get(exam_id)
    if exam is None:
        raise HTTPException(status_code=404, detail="Exam bulunamadı.")
    flashcards = flashcard_repository.list_by_exam(exam_id)
    return [
        FlashcardResponseSchema(
            card_id=card.CardId,
            exam_id=card.ExamId,
            front_side=card.FrontSide,
            back_side=card.BackSide,
            status=card.Status,
        )
        for card in flashcards
    ]


@router.post("/{exam_id}/generate-ai-cards", response_model=list[FlashcardResponseSchema])
async def generate_ai_cards_for_exam(exam_id: str, db: Session = Depends(get_db)) -> list[FlashcardResponseSchema]:
    exam_repository = ExamRepository(db)
    flashcard_repository = FlashcardRepository(db)
    exam = exam_repository.get(exam_id)
    if exam is None:
        raise HTTPException(status_code=404, detail="Exam bulunamadı.")

    try:
        ai_cards = await generate_flashcards_raw(exam.CourseName)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=f"AI servisi hatası: {str(e)}")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"AI yanıtı işleme hatası: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Beklenmeyen hata: {str(e)}")

    created = []
    for item in ai_cards:
        front = item.get("soru")
        back = item.get("cevap")
        if not front or not back:
            continue
        from app.domain.models import Flashcard

        card = Flashcard.create(exam_id=exam.ExamId, front_side=front, back_side=back)
        saved = flashcard_repository.add(card)
        created.append(saved)

    return [
        FlashcardResponseSchema(
            card_id=c.CardId,
            exam_id=c.ExamId,
            front_side=c.FrontSide,
            back_side=c.BackSide,
            status=c.Status,
        )
        for c in created
    ]

