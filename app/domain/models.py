from __future__ import annotations
from dataclasses import dataclass
from datetime import date
from typing import List
from uuid import uuid4

from sqlalchemy import Column, Date, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Enum as SqlEnum

from app.core.config import Base
from app.domain.enums import LeitnerBox


@dataclass
class StudySession:
    remaining_days: int
    daily_target: int
    completed_today: int


class Exam(Base):
    __tablename__ = "exams"

    ExamId: Mapped[str] = mapped_column(String(36), primary_key=True, index=True)
    CourseName: Mapped[str] = mapped_column(String(100), nullable=False)
    ExamDate: Mapped[date] = mapped_column(Date, nullable=False)
    flashcards = relationship(
        "Flashcard",
        back_populates="exam",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    @classmethod
    def create(cls, course_name: str, exam_date: date) -> "Exam":
        return cls(
            ExamId=str(uuid4()),
            CourseName=course_name.strip(),
            ExamDate=exam_date,
        )

    def is_future(self) -> bool:
        return self.ExamDate > date.today()


class Flashcard(Base):
    __tablename__ = "flashcards"

    CardId: Mapped[str] = mapped_column(String(36), primary_key=True, index=True)
    ExamId: Mapped[str] = mapped_column(String(36), ForeignKey("exams.ExamId", ondelete="CASCADE"), nullable=False)
    FrontSide: Mapped[str] = mapped_column(String(500), nullable=False)
    BackSide: Mapped[str] = mapped_column(String, nullable=False)
    Status: Mapped[LeitnerBox] = mapped_column(
        SqlEnum(LeitnerBox, native_enum=False, length=50),
        nullable=False,
        default=LeitnerBox.Box1,
    )
    exam: Mapped[Exam] = relationship("Exam", back_populates="flashcards")

    @classmethod
    def create(cls, exam_id: str, front_side: str, back_side: str) -> "Flashcard":
        return cls(
            CardId=str(uuid4()),
            ExamId=exam_id,
            FrontSide=front_side.strip(),
            BackSide=back_side.strip(),
            Status=LeitnerBox.Box1,
        )
