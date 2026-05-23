from datetime import date
from typing import Optional

from pydantic import BaseModel, constr, validator

from app.domain.enums import LeitnerBox


class ExamCreateSchema(BaseModel):
    course_name: constr(strip_whitespace=True, min_length=1, max_length=100)
    exam_date: date

    @validator("exam_date")
    def ensure_future_date(cls, value: date) -> date:
        if value <= date.today():
            raise ValueError("ExamDate gelecekte olmalıdır.")
        return value


class ExamUpdateSchema(BaseModel):
    exam_date: date

    @validator("exam_date")
    def ensure_future_date(cls, value: date) -> date:
        if value <= date.today():
            raise ValueError("ExamDate gelecekte olmalıdır.")
        return value


class ExamResponseSchema(BaseModel):
    exam_id: str
    course_name: str
    exam_date: date
    remaining_days: int
    daily_target: int
    flashcard_count: int = 0
    mastered_count: int = 0

    class Config:
        from_attributes = True


class FlashcardCreateSchema(BaseModel):
    exam_id: str
    front_side: constr(strip_whitespace=True, min_length=1, max_length=500)
    back_side: constr(strip_whitespace=True, min_length=1)


class LeitnerUpdateSchema(BaseModel):
    known: bool


class FlashcardResponseSchema(BaseModel):
    card_id: str
    exam_id: str
    front_side: str
    back_side: str
    status: LeitnerBox

    class Config:
        from_attributes = True


class StudySessionResponseSchema(BaseModel):
    remaining_days: int
    daily_target: int
    flashcard_count: int = 0
    mastered_count: int = 0


class FlashcardListResponseSchema(BaseModel):
    flashcards: list[FlashcardResponseSchema]
