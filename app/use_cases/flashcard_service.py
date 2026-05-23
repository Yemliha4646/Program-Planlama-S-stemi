"""Flashcard iş mantığı servisi — kart CRUD ve Leitner kutu geçişleri."""

from app.domain.enums import LeitnerBox
from app.domain.models import Exam, Flashcard
from app.infrastructure.repositories import FlashcardRepository


class FlashcardService:
    """Flashcard oluşturma, silme ve Leitner sistemi kutu geçiş iş mantığı."""

    def __init__(self, flashcard_repository: FlashcardRepository) -> None:
        self.flashcard_repository = flashcard_repository

    def create_flashcard(self, exam: Exam, front_side: str, back_side: str) -> Flashcard:
        """Yeni bir flashcard oluşturur. Ön ve arka yüz doğrulaması yapar."""
        normalized_front = front_side.strip()
        normalized_back = back_side.strip()
        if not normalized_front:
            raise ValueError("Soru alanı (ön yüz) boş bırakılamaz.")
        if len(normalized_front) > 500:
            raise ValueError("Soru alanı en fazla 500 karakter olabilir.")
        if not normalized_back:
            raise ValueError("Cevap alanı (arka yüz) boş bırakılamaz.")

        flashcard = Flashcard.create(
            exam_id=exam.ExamId,
            front_side=normalized_front,
            back_side=normalized_back,
        )
        return self.flashcard_repository.add(flashcard)

    def update_leitner(self, flashcard: Flashcard, known: bool) -> Flashcard:
        """Leitner kutu geçişini uygular.

        Bildim (known=True): Box1→Box2→Box3→Mastered
        Bilemedim (known=False): Herhangi bir kutudan Box1'e geri döner.
        """
        if known:
            if flashcard.Status == LeitnerBox.Box1:
                flashcard.Status = LeitnerBox.Box2
            elif flashcard.Status == LeitnerBox.Box2:
                flashcard.Status = LeitnerBox.Box3
            elif flashcard.Status == LeitnerBox.Box3:
                flashcard.Status = LeitnerBox.Mastered
            # Mastered → known=True: zaten en üst seviye, değişiklik yapma
        else:
            flashcard.Status = LeitnerBox.Box1
        return self.flashcard_repository.update(flashcard)

    def delete_flashcard(self, flashcard: Flashcard) -> None:
        """Flashcard'ı siler."""
        self.flashcard_repository.delete(flashcard)
