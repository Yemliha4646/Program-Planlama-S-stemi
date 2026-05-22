from datetime import date

from app.domain.models import Exam, Flashcard, StudySession
from app.infrastructure.repositories import ExamRepository, FlashcardRepository


class ExamService:
    def __init__(self, exam_repository: ExamRepository, flashcard_repository: FlashcardRepository) -> None:
        self.exam_repository = exam_repository
        self.flashcard_repository = flashcard_repository

    def create_exam(self, course_name: str, exam_date: date) -> Exam:
        normalized_course_name = course_name.strip()
        if not normalized_course_name:
            raise ValueError("CourseName boş olamaz.")
        if len(normalized_course_name) > 100:
            raise ValueError("CourseName maksimum 100 karakter olmalıdır.")
        if exam_date <= date.today():
            raise ValueError("ExamDate gelecekte olmalıdır.")

        exam = Exam.create(course_name=normalized_course_name, exam_date=exam_date)
        return self.exam_repository.add(exam)

    def get_exam(self, exam_id: str) -> Exam | None:
        return self.exam_repository.get(exam_id)

    def list_exams(self) -> list[Exam]:
        return self.exam_repository.list()

    def update_exam_date(self, exam: Exam, new_date: date) -> Exam:
        if new_date <= date.today():
            raise ValueError("ExamDate gelecekte olmalıdır.")
        exam.ExamDate = new_date
        return self.exam_repository.save(exam)

    def delete_exam(self, exam: Exam) -> None:
        self.exam_repository.delete(exam)

    def build_study_session(self, exam: Exam, flashcards: list[Flashcard], completed_today: int = 0) -> StudySession:
        from app.domain.enums import LeitnerBox
        remaining_days = max((exam.ExamDate - date.today()).days, 0)
        active_cards = [c for c in flashcards if c.Status != LeitnerBox.Mastered]
        total_active = len(active_cards)
        if total_active == 0:
            daily_target = 0
        elif remaining_days <= 0:
            daily_target = total_active
        else:
            daily_target = max((total_active + remaining_days - 1) // remaining_days, 1)
        return StudySession(
            remaining_days=remaining_days,
            daily_target=daily_target,
            completed_today=max(completed_today, 0),
        )
