const apiRoot = "/api";
const examForm = document.getElementById("exam-form");
const examsList = document.getElementById("exams-list");
const detailsSection = document.getElementById("details-section");
const selectedExamElement = document.getElementById("selected-exam");
const remainingDaysElement = document.getElementById("remaining-days");
const dailyTargetElement = document.getElementById("daily-target");
const completedTodayElement = document.getElementById("completed-today");
const flashcardForm = document.getElementById("flashcard-form");
const flashcardsList = document.getElementById("flashcards-list");

let currentExam = null;

async function fetchExams() {
  const response = await fetch(`${apiRoot}/exams`);
  const exams = await response.json();
  renderExamCards(exams);
}

function renderExamCards(exams) {
  examsList.innerHTML = exams
    .map(
      (exam) => `
      <button class="w-full rounded-3xl border border-slate-700 bg-slate-900 px-5 py-4 text-left transition hover:border-emerald-400 hover:bg-slate-800"
        onclick="selectExam('${exam.exam_id}')">
        <div class="flex items-center justify-between">
          <span class="font-bold text-white">${escapeHtml(exam.course_name)}</span>
          <span class="text-slate-400">${exam.remaining_days} gün</span>
        </div>
        <p class="mt-2 text-slate-400">Günlük hedef: ${exam.daily_target}</p>
      </button>
    `
    )
    .join("");
}

function escapeHtml(value) {
  return value
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

window.selectExam = async function (examId) {
  const response = await fetch(`${apiRoot}/exams/${examId}`);
  const exam = await response.json();
  currentExam = exam;
  selectedExamElement.textContent = `${exam.course_name} - ${exam.exam_date}`;
  remainingDaysElement.textContent = exam.remaining_days;
  dailyTargetElement.textContent = exam.daily_target;
  completedTodayElement.textContent = exam.completed_today;
  detailsSection.classList.remove("hidden");
  loadFlashcards(examId);
};

async function loadFlashcards(examId) {
  const response = await fetch(`${apiRoot}/exams/${examId}/flashcards`);
  const flashcards = await response.json();
  flashcardsList.innerHTML = flashcards
    .map(
      (card) => `
      <div class="card-container">
        <div class="flashcard rounded-3xl bg-slate-900 text-slate-100 shadow-xl shadow-black/20" onclick="toggleCard(this)">
          <div class="card-face">
            <p class="text-slate-400">Ön yüz</p>
            <h3 class="mt-4 text-xl font-semibold">${escapeHtml(card.front_side)}</h3>
            <p class="mt-4 text-slate-300">${escapeHtml(card.front_side.length > 200 ? card.front_side.slice(0, 200) + '...' : '')}</p>
          </div>
          <div class="card-face card-back bg-slate-950">
            <p class="text-slate-400">Arka yüz</p>
            <p class="mt-4 text-xl font-semibold">${escapeHtml(card.back_side)}</p>
            <p class="mt-4 text-emerald-400">Durum: ${card.status}</p>
          </div>
          <div class="card-actions p-4 border-t border-slate-800 mt-auto flex gap-3 bg-slate-900 rounded-b-3xl">
            <button class="rounded-2xl bg-emerald-500 px-4 py-2 font-semibold text-slate-950" onclick="event.stopPropagation(); markKnown('${card.card_id}')">Bildim</button>
            <button class="rounded-2xl bg-rose-500 px-4 py-2 font-semibold text-white" onclick="event.stopPropagation(); markUnknown('${card.card_id}')">Bilemedim</button>
            <button class="rounded-2xl bg-slate-700 px-4 py-2 text-slate-100" onclick="event.stopPropagation(); deleteCard('${card.card_id}')">Sil</button>
          </div>
        </div>
      </div>
    `
    )
    .join("");
}

window.toggleCard = function (element) {
  element.classList.toggle("flipped");
};

async function markKnown(cardId) {
  await updateLeitner(cardId, true);
}

async function markUnknown(cardId) {
  await updateLeitner(cardId, false);
}

async function updateLeitner(cardId, known) {
  await fetch(`${apiRoot}/flashcards/${cardId}/leitner`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ known }),
  });
  if (currentExam) {
    await selectExam(currentExam.exam_id);
  }
}

async function deleteCard(cardId) {
  await fetch(`${apiRoot}/flashcards/${cardId}`, {
    method: "DELETE",
  });
  if (currentExam) {
    await selectExam(currentExam.exam_id);
  }
}

examForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const courseName = document.getElementById("exam-course").value;
  const examDate = document.getElementById("exam-date").value;

  await fetch(`${apiRoot}/exams`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ course_name: courseName, exam_date: examDate }),
  });

  examForm.reset();
  await fetchExams();
});

flashcardForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (!currentExam) {
    return;
  }

  const front = document.getElementById("card-front").value;
  const back = document.getElementById("card-back").value;

  await fetch(`${apiRoot}/flashcards`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ exam_id: currentExam.exam_id, front_side: front, back_side: back }),
  });

  flashcardForm.reset();
  await selectExam(currentExam.exam_id);
});

fetchExams();

// Attach AI generate button handler
const aiBtn = document.getElementById("generate-ai-btn");
if (aiBtn) {
  aiBtn.addEventListener("click", async (e) => {
    e.preventDefault();
    if (!currentExam) {
      alert("Önce bir sınav seçin.");
      return;
    }
    aiBtn.disabled = true;
    const prev = aiBtn.innerHTML;
    aiBtn.innerHTML = "Üretiliyor...";
    try {
      const resp = await fetch(`${apiRoot}/exams/${currentExam.exam_id}/generate-ai-cards`, { method: "POST" });
      if (!resp.ok) {
        const txt = await resp.text();
        throw new Error(txt || "Sunucu hatası");
      }
      await selectExam(currentExam.exam_id);
    } catch (err) {
      alert("AI üretim hatası: " + err.message);
    } finally {
      aiBtn.disabled = false;
      aiBtn.innerHTML = prev;
    }
  });
}
