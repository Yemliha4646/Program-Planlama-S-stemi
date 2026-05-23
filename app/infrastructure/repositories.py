"""Veritabanı repository katmanı — veri erişim işlemlerini soyutlar."""

from sqlalchemy.orm import Session

from app.domain.models import Exam, Flashcard


class ExamRepository:
    """Sınav varlığı için veri erişim katmanı (Repository Pattern)."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def add(self, exam: Exam) -> Exam:
        """Yeni bir sınavı veritabanına ekler."""
        self.db.add(exam)
        self.db.commit()
        self.db.refresh(exam)
        return exam

    def get(self, exam_id: str) -> Exam | None:
        """Verilen ID'ye sahip sınavı getirir, bulunamazsa None döner."""
        return self.db.get(Exam, exam_id)

    def list(self) -> list[Exam]:
        """Tüm sınavları tarihe göre sıralı listeler."""
        return self.db.query(Exam).order_by(Exam.ExamDate).all()

    def delete(self, exam: Exam) -> None:
        """Sınavı ve ilişkili kartlarını siler (Cascade Delete)."""
        self.db.delete(exam)
        self.db.commit()

    def update(self, exam: Exam) -> Exam:
        """Mevcut bir sınavın değişikliklerini veritabanına yansıtır."""
        self.db.add(exam)
        self.db.commit()
        self.db.refresh(exam)
        return exam


class FlashcardRepository:
    """Flashcard varlığı için veri erişim katmanı (Repository Pattern)."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def add(self, flashcard: Flashcard) -> Flashcard:
        """Yeni bir flashcard'ı veritabanına ekler."""
        self.db.add(flashcard)
        self.db.commit()
        self.db.refresh(flashcard)
        return flashcard

    def get(self, card_id: str) -> Flashcard | None:
        """Verilen ID'ye sahip flashcard'ı getirir, bulunamazsa None döner."""
        return self.db.get(Flashcard, card_id)

    def list_by_exam(self, exam_id: str) -> list[Flashcard]:
        """Belirli bir sınava ait tüm flashcard'ları listeler."""
        return (
            self.db.query(Flashcard)
            .filter(Flashcard.ExamId == exam_id)
            .order_by(Flashcard.CardId)
            .all()
        )

    def delete(self, flashcard: Flashcard) -> None:
        """Flashcard'ı veritabanından siler."""
        self.db.delete(flashcard)
        self.db.commit()

    def update(self, flashcard: Flashcard) -> Flashcard:
        """Mevcut bir flashcard'ın değişikliklerini veritabanına yansıtır."""
        self.db.add(flashcard)
        self.db.commit()
        self.db.refresh(flashcard)
        return flashcard
