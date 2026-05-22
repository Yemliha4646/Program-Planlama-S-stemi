from sqlalchemy.orm import Session

from app.domain.models import Exam, Flashcard


class ExamRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def add(self, exam: Exam) -> Exam:
        self.db.add(exam)
        self.db.commit()
        self.db.refresh(exam)
        return exam

    def get(self, exam_id: str) -> Exam | None:
        return self.db.get(Exam, exam_id)

    def list(self) -> list[Exam]:
        return self.db.query(Exam).order_by(Exam.ExamDate).all()

    def delete(self, exam: Exam) -> None:
        self.db.delete(exam)
        self.db.commit()

    def save(self, exam: Exam) -> Exam:
        self.db.add(exam)
        self.db.commit()
        self.db.refresh(exam)
        return exam


class FlashcardRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def add(self, flashcard: Flashcard) -> Flashcard:
        self.db.add(flashcard)
        self.db.commit()
        self.db.refresh(flashcard)
        return flashcard

    def get(self, card_id: str) -> Flashcard | None:
        return self.db.get(Flashcard, card_id)

    def list_by_exam(self, exam_id: str) -> list[Flashcard]:
        return (
            self.db.query(Flashcard)
            .filter(Flashcard.ExamId == exam_id)
            .order_by(Flashcard.CardId)
            .all()
        )

    def delete(self, flashcard: Flashcard) -> None:
        self.db.delete(flashcard)
        self.db.commit()

    def save(self, flashcard: Flashcard) -> Flashcard:
        self.db.add(flashcard)
        self.db.commit()
        self.db.refresh(flashcard)
        return flashcard
