"""Sınav iş mantığı servisi — sınav CRUD ve çalışma oturumu hesaplama."""

from datetime import date
from math import ceil

from app.domain.enums import LeitnerBox
from app.domain.models import Exam, Flashcard, StudySession
from app.infrastructure.repositories import ExamRepository, FlashcardRepository


class ExamService:
    """Sınav oluşturma, güncelleme, silme ve çalışma oturumu hesaplama iş mantığı."""

    def __init__(self, exam_repository: ExamRepository, flashcard_repository: FlashcardRepository) -> None:
        self.exam_repository = exam_repository
        self.flashcard_repository = flashcard_repository

    def create_exam(self, course_name: str, exam_date: date) -> Exam:
        """Yeni bir sınav oluşturur. Ders adı ve tarih doğrulaması yapar."""
        normalized_course_name = course_name.strip()
        if not normalized_course_name:
            raise ValueError("Ders adı boş bırakılamaz.")
        if len(normalized_course_name) > 100:
            raise ValueError("Ders adı en fazla 100 karakter olabilir.")
        if exam_date <= date.today():
            raise ValueError("Sınav tarihi bugünden ileri bir tarih olmalıdır.")

        exam = Exam.create(course_name=normalized_course_name, exam_date=exam_date)
        return self.exam_repository.add(exam)

    def get_exam(self, exam_id: str) -> Exam | None:
        """Verilen ID'ye sahip sınavı getirir."""
        return self.exam_repository.get(exam_id)

    def list_exams(self) -> list[Exam]:
        """Tüm sınavları listeler."""
        return self.exam_repository.list()

    def update_exam_date(self, exam: Exam, new_date: date) -> Exam:
        """Sınav tarihini günceller. Yeni tarih gelecekte olmalıdır."""
        if new_date <= date.today():
            raise ValueError("Sınav tarihi bugünden ileri bir tarih olmalıdır.")
        exam.ExamDate = new_date
        return self.exam_repository.update(exam)

    def delete_exam(self, exam: Exam) -> None:
        """Sınavı ve ilişkili kartlarını siler."""
        self.exam_repository.delete(exam)

    def build_study_session(
        self, exam: Exam, flashcards: list[Flashcard], completed_today: int = 0
    ) -> StudySession:
        """Günlük çalışma oturumunu hesaplar.

        Kalan gün 0 ise tüm aktif kartlar o günün hedefi olarak döner.
        Aktif kart yoksa hedef 0'dır.
        """
        today = date.today()
        remaining_days = max((exam.ExamDate - today).days, 0)

        # Sadece Mastered olmayan (aktif) kartları say
        active_count = sum(1 for c in flashcards if c.Status != LeitnerBox.Mastered)

        if active_count == 0:
            daily_target = 0
        elif remaining_days == 0:
            # Sınav günü geldi — tüm aktif kartlar hedef
            daily_target = active_count
        else:
            # Ceiling division: 5 kart / 3 gün = 2 (tavan), böylece hiçbir kart atlanmaz
            daily_target = ceil(active_count / remaining_days)

        return StudySession(
            remaining_days=remaining_days,
            daily_target=daily_target,
            completed_today=max(completed_today, 0),
        )
