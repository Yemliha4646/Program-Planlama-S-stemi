from datetime import date
from typing import Annotated

from pydantic import BaseModel, ConfigDict, StringConstraints, field_validator

from app.domain.enums import LeitnerBox


class ExamCreateSchema(BaseModel):
    """Yeni sınav oluşturma isteği için giriş şeması."""
    course_name: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)]
    exam_date: date

    @field_validator("exam_date")
    @classmethod
    def ensure_future_date(cls, value: date) -> date:
        if value <= date.today():
            raise ValueError("ExamDate gelecekte olmalıdır.")
        return value


class ExamUpdateSchema(BaseModel):
    """Sınav tarihi güncelleme isteği için giriş şeması."""
    exam_date: date

    @field_validator("exam_date")
    @classmethod
    def ensure_future_date(cls, value: date) -> date:
        if value <= date.today():
            raise ValueError("ExamDate gelecekte olmalıdır.")
        return value


class ExamResponseSchema(BaseModel):
    """Sınav yanıt şeması — sınav bilgileri ve planlama metrikleri içerir."""
    exam_id: str
    course_name: str
    exam_date: date
    remaining_days: int
    daily_target: int
    flashcard_count: int = 0
    mastered_count: int = 0

    model_config = ConfigDict(from_attributes=True)


class FlashcardCreateSchema(BaseModel):
    """Yeni flashcard oluşturma isteği için giriş şeması."""
    exam_id: str
    front_side: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=500)]
    back_side: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class LeitnerUpdateSchema(BaseModel):
    """Leitner kutu güncelleme isteği — Bildim/Bilemedim."""
    known: bool


class FlashcardResponseSchema(BaseModel):
    """Flashcard yanıt şeması."""
    card_id: str
    exam_id: str
    front_side: str
    back_side: str
    status: LeitnerBox

    model_config = ConfigDict(from_attributes=True)


class StudySessionResponseSchema(BaseModel):
    """Çalışma oturumu yanıt şeması."""
    remaining_days: int
    daily_target: int
    flashcard_count: int = 0
    mastered_count: int = 0


class FlashcardListResponseSchema(BaseModel):
    """Flashcard listesi sarmalayıcı şeması."""
    flashcards: list[FlashcardResponseSchema]
