/* ═══════════════════════════════════════════════════
   Program Planlama Sistemi — Frontend
   ═══════════════════════════════════════════════════ */

const apiRoot = "/api";

// DOM refs
const examForm         = document.getElementById("exam-form");
const examsList        = document.getElementById("exams-list");
const detailsSection   = document.getElementById("details-section");
const selectedExamEl   = document.getElementById("selected-exam");
const remainingDaysEl  = document.getElementById("remaining-days");
const dailyTargetEl    = document.getElementById("daily-target");
const totalCardsEl     = document.getElementById("total-cards");
const completedTodayEl = document.getElementById("completed-today");
const flashcardForm    = document.getElementById("flashcard-form");
const flashcardsList   = document.getElementById("flashcards-list");
const aiBtn            = document.getElementById("generate-ai-btn");

let currentExam = null;

// ─── Yardımcılar ───────────────────────────────────

function escapeHtml(value) {
  return value
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

/** Tarihi "27 Mayıs 2026" formatına çevirir */
function formatDateTR(isoStr) {
  const months = [
    "Ocak","Şubat","Mart","Nisan","Mayıs","Haziran",
    "Temmuz","Ağustos","Eylül","Ekim","Kasım","Aralık"
  ];
  const [y, m, d] = isoStr.split("-").map(Number);
  return `${d} ${months[m - 1]} ${y}`;
}

/** Bugünün tarihini YYYY-MM-DD formatında döndürür */
function todayISO() {
  const d = new Date();
  return d.toISOString().split("T")[0];
}

/** Leitner kutusu etiketini döndürür */
function getLevelLabel(status) {
  const map = {
    Box1: "📦 Kutu 1 — Yeni",
    Box2: "📦 Kutu 2 — Öğreniliyor",
    Box3: "📦 Kutu 3 — Pekiştiriliyor",
    Mastered: "✅ Tamamlandı",
  };
  return map[status] || status;
}

/** Leitner kutusuna göre CSS badge sınıfı */
function getBadgeClass(status) {
  const map = {
    Box1: "badge-box1",
    Box2: "badge-box2",
    Box3: "badge-box3",
    Mastered: "badge-mastered",
  };
  return map[status] || "";
}

/** Kalan güne göre renk sınıfı */
function getDaysColor(days) {
  if (days <= 3)  return "text-rose-400";
  if (days <= 7)  return "text-amber-400";
  return "text-emerald-400";
}

/** Kullanıcı dostu hata mesajı */
function friendlyError(err) {
  if (!err) return "Bilinmeyen bir hata oluştu.";
  const msg = typeof err === "string" ? err : err.message || String(err);
  if (msg.includes("Failed to fetch") || msg.includes("NetworkError"))
    return "Sunucuya bağlanılamadı. Sunucu çalışıyor mu?";
  if (msg.includes("401") || msg.includes("API key"))
    return "API anahtarı geçersiz veya eksik.";
  return msg;
}

// ─── Tarih Validasyonu ─────────────────────────────

(function setMinDate() {
  const dateInput = document.getElementById("exam-date");
  if (dateInput) {
    // Yarın en erken seçilebilir tarih
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    dateInput.min = tomorrow.toISOString().split("T")[0];
  }
})();

// ─── SINAV İŞLEMLERİ ──────────────────────────────

async function fetchExams() {
  try {
    const response = await fetch(`${apiRoot}/exams`);
    if (!response.ok) throw new Error(`Sınavlar yüklenemedi (${response.status})`);
    const exams = await response.json();
    renderExamCards(exams);
  } catch (err) {
    examsList.innerHTML = `
      <div class="rounded-xl bg-rose-500/10 border border-rose-500/20 p-4 text-center text-rose-400 text-sm">
        ⚠️ ${friendlyError(err)}
      </div>`;
  }
}

function renderExamCards(exams) {
  if (exams.length === 0) {
    examsList.innerHTML = `
      <div class="flex flex-col items-center justify-center py-10 text-center">
        <p class="text-4xl mb-3">📝</p>
        <p class="text-slate-400 font-medium">Henüz sınav eklenmedi</p>
        <p class="text-slate-500 text-sm mt-1">Soldaki formdan ilk sınavınızı oluşturun.</p>
      </div>`;
    return;
  }

  examsList.innerHTML = exams
    .map((exam) => {
      const daysColor = getDaysColor(exam.remaining_days);
      const total     = exam.flashcard_count || 0;
      const mastered  = exam.mastered_count  || 0;
      const pct       = total > 0 ? Math.round((mastered / total) * 100) : 0;

      return `
      <div class="flex items-stretch gap-2 group">
        <button class="flex-1 rounded-xl border border-slate-800 bg-slate-950/60 px-5 py-4 text-left transition
                       hover:border-emerald-400/50 hover:bg-slate-800/60"
          onclick="selectExam('${exam.exam_id}')">
          <div class="flex items-center justify-between">
            <span class="font-semibold text-white">${escapeHtml(exam.course_name)}</span>
            <span class="${daysColor} text-sm font-bold">${exam.remaining_days} gün</span>
          </div>
          <p class="mt-1.5 text-xs text-slate-500">${formatDateTR(exam.exam_date)} · ${total} kart · Hedef: ${exam.daily_target}/gün</p>
          ${total > 0 ? `
          <div class="mt-2.5">
            <div class="flex items-center justify-between text-[11px] text-slate-500 mb-1">
              <span>İlerleme</span>
              <span class="font-semibold text-emerald-400">${pct}%</span>
            </div>
            <div class="progress-track">
              <div class="progress-fill" style="width:${pct}%"></div>
            </div>
          </div>` : ""}
        </button>
        <button
          onclick="deleteExam('${exam.exam_id}')"
          class="flex items-center justify-center rounded-xl bg-rose-500/10 border border-rose-500/20 px-3.5 text-rose-400 font-bold text-lg transition hover:bg-rose-500/20 hover:border-rose-400 active:scale-95"
          title="Sınavı Sil">
          ✕
        </button>
      </div>`;
    })
    .join("");
}

window.deleteExam = async function (examId) {
  if (!confirm("Bu sınavı ve tüm flashcard'larını silmek istediğinize emin misiniz?")) return;
  try {
    const resp = await fetch(`${apiRoot}/exams/${examId}`, { method: "DELETE" });
    if (!resp.ok) throw new Error("Silme işlemi başarısız.");
    if (currentExam && currentExam.exam_id === examId) {
      currentExam = null;
      detailsSection.classList.add("hidden");
    }
    await fetchExams();
  } catch (err) {
    alert("Silme hatası: " + friendlyError(err));
  }
};

window.selectExam = async function (examId) {
  try {
    const response = await fetch(`${apiRoot}/exams/${examId}`);
    if (!response.ok) throw new Error(`Sınav yüklenemedi (${response.status})`);
    const exam = await response.json();
    currentExam = exam;

    selectedExamEl.textContent = `${exam.course_name} — ${formatDateTR(exam.exam_date)}`;

    // Kalan gün — acil durum renklendirmesi
    remainingDaysEl.textContent = exam.remaining_days;
    remainingDaysEl.className = `mt-1.5 text-3xl font-bold ${getDaysColor(exam.remaining_days)}`;

    dailyTargetEl.textContent    = exam.daily_target;
    totalCardsEl.textContent     = exam.flashcard_count || 0;
    completedTodayEl.textContent = exam.mastered_count  || 0;

    detailsSection.classList.remove("hidden");
    await loadFlashcards(examId);
    await fetchExams(); // Sınav listesini de güncelle
  } catch (err) {
    alert("Sınav detayları yüklenemedi: " + friendlyError(err));
  }
};

// ─── FLASHCARD İŞLEMLERİ ──────────────────────────

function updateStats(flashcards) {
  const unknown  = flashcards.filter((c) => c.status === "Box1").length;
  const known    = flashcards.filter((c) => c.status === "Box2" || c.status === "Box3").length;
  const mastered = flashcards.filter((c) => c.status === "Mastered").length;

  document.getElementById("stat-unknown").textContent  = unknown;
  document.getElementById("stat-known").textContent    = known;
  document.getElementById("stat-mastered").textContent = mastered;
}

async function loadFlashcards(examId) {
  try {
    const response = await fetch(`${apiRoot}/exams/${examId}/flashcards`);
    if (!response.ok) throw new Error(`Flashcard'lar yüklenemedi (${response.status})`);
    const flashcards = await response.json();

    updateStats(flashcards);

    if (flashcards.length === 0) {
      flashcardsList.innerHTML = `
        <div class="flex flex-col items-center justify-center py-8 text-center">
          <p class="text-3xl mb-2">🃏</p>
          <p class="text-slate-400 font-medium text-sm">Henüz flashcard yok</p>
          <p class="text-slate-500 text-xs mt-1">Formu kullanarak veya yapay zekâ ile oluşturun.</p>
        </div>`;
      return;
    }

    flashcardsList.innerHTML = flashcards
      .map(
        (card) => `
    <div class="card-container" style="min-height:200px;">
      <div class="flashcard rounded-xl bg-slate-950 border border-slate-800 text-slate-100 shadow-lg" onclick="toggleCard(this)" style="min-height:200px;">

        <!-- ÖN YÜZ -->
        <div class="card-face p-5">
          <div class="flex items-center justify-between mb-3">
            <span class="text-[11px] font-semibold uppercase tracking-widest text-slate-500">Ön yüz</span>
            <span class="rounded-full px-2.5 py-0.5 text-[11px] font-semibold ${getBadgeClass(card.status)}">${getLevelLabel(card.status)}</span>
          </div>
          <h3 class="text-base font-semibold leading-relaxed">${escapeHtml(card.front_side)}</h3>
          <p class="mt-4 text-xs text-slate-600 italic">Cevabı görmek için tıkla →</p>
        </div>

        <!-- ARKA YÜZ -->
        <div class="card-face card-back bg-slate-900 border border-slate-700 p-5 flex flex-col justify-between">
          <div>
            <p class="text-[11px] font-semibold uppercase tracking-widest text-slate-500 mb-3">Arka yüz</p>
            <p class="text-base font-semibold leading-relaxed">${escapeHtml(card.back_side)}</p>
          </div>
          <div class="card-actions gap-2 pt-4 border-t border-slate-800 mt-4" onclick="event.stopPropagation()">
            <button class="flex-1 rounded-lg bg-emerald-500 py-2 font-semibold text-slate-950 text-sm transition hover:bg-emerald-400 active:scale-95" onclick="markKnown('${card.card_id}')">✓ Bildim</button>
            <button class="flex-1 rounded-lg bg-rose-500 py-2 font-semibold text-white text-sm transition hover:bg-rose-400 active:scale-95" onclick="markUnknown('${card.card_id}')">✗ Bilemedim</button>
            <button class="rounded-lg bg-slate-700 px-3 py-2 text-slate-300 text-sm transition hover:bg-slate-600 active:scale-95" onclick="deleteCard('${card.card_id}')" title="Kartı Sil">🗑</button>
          </div>
        </div>

      </div>
    </div>`
      )
      .join("");
  } catch (err) {
    flashcardsList.innerHTML = `
      <div class="rounded-xl bg-rose-500/10 border border-rose-500/20 p-4 text-center text-rose-400 text-sm">
        ⚠️ ${friendlyError(err)}
      </div>`;
  }
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
  try {
    const resp = await fetch(`${apiRoot}/flashcards/${cardId}/leitner`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ known }),
    });
    if (!resp.ok) throw new Error("Güncelleme başarısız.");
    if (currentExam) await selectExam(currentExam.exam_id);
  } catch (err) {
    alert("Leitner güncelleme hatası: " + friendlyError(err));
  }
}

async function deleteCard(cardId) {
  try {
    const resp = await fetch(`${apiRoot}/flashcards/${cardId}`, { method: "DELETE" });
    if (!resp.ok) throw new Error("Silme başarısız.");
    if (currentExam) await selectExam(currentExam.exam_id);
  } catch (err) {
    alert("Kart silme hatası: " + friendlyError(err));
  }
}

// ─── FORM EVENT'LERİ ──────────────────────────────

examForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const courseName = document.getElementById("exam-course").value.trim();
  const examDate   = document.getElementById("exam-date").value;

  if (!courseName || !examDate) return;

  // Client-side tarih kontrolü
  if (examDate <= todayISO()) {
    alert("Sınav tarihi gelecekte olmalıdır.");
    return;
  }

  try {
    const resp = await fetch(`${apiRoot}/exams`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ course_name: courseName, exam_date: examDate }),
    });
    if (!resp.ok) {
      const data = await resp.json().catch(() => null);
      throw new Error(data?.detail || `Sınav oluşturulamadı (${resp.status})`);
    }
    examForm.reset();
    await fetchExams();
  } catch (err) {
    alert("Sınav oluşturma hatası: " + friendlyError(err));
  }
});

flashcardForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (!currentExam) {
    alert("Önce bir sınav seçin.");
    return;
  }

  const front = document.getElementById("card-front").value.trim();
  const back  = document.getElementById("card-back").value.trim();

  if (!front || !back) return;

  try {
    const resp = await fetch(`${apiRoot}/flashcards`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ exam_id: currentExam.exam_id, front_side: front, back_side: back }),
    });
    if (!resp.ok) {
      const data = await resp.json().catch(() => null);
      throw new Error(data?.detail || `Kart oluşturulamadı (${resp.status})`);
    }
    flashcardForm.reset();
    await selectExam(currentExam.exam_id);
  } catch (err) {
    alert("Kart oluşturma hatası: " + friendlyError(err));
  }
});

// ─── AI KART ÜRETİMİ ──────────────────────────────

if (aiBtn) {
  aiBtn.addEventListener("click", async () => {
    if (!currentExam) {
      alert("Önce bir sınav seçin.");
      return;
    }
    aiBtn.disabled = true;
    const prev = aiBtn.innerHTML;
    aiBtn.innerHTML = '<span class="animate-pulse">⏳ Yapay zekâ düşünüyor…</span>';

    try {
      const resp = await fetch(`${apiRoot}/exams/${currentExam.exam_id}/generate-ai-cards`, { method: "POST" });
      if (!resp.ok) {
        const data = await resp.json().catch(() => null);
        throw new Error(data?.detail || "Sunucu hatası");
      }
      await selectExam(currentExam.exam_id);
    } catch (err) {
      alert("Yapay zekâ kart üretimi başarısız oldu.\n" + friendlyError(err));
    } finally {
      aiBtn.disabled = false;
      aiBtn.innerHTML = prev;
    }
  });
}

// ─── BAŞLANGIÇ ─────────────────────────────────────
fetchExams();
