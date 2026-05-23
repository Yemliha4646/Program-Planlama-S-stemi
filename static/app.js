/* ═══════════════════════════════════════════════════
   Program Planlama Sistemi — Frontend Logic
   ═══════════════════════════════════════════════════ */

const apiRoot = "/api";

// DOM referansları
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

// ─── Yardımcı Fonksiyonlar ───────────────────────────────

function escapeHtml(value) {
  if (!value) return "";
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

/** ISO tarihini "27 Mayıs 2026" formatına çevirir */
function formatDateTR(isoStr) {
  if (!isoStr) return "";
  const months = ["Ocak","Şubat","Mart","Nisan","Mayıs","Haziran",
                  "Temmuz","Ağustos","Eylül","Ekim","Kasım","Aralık"];
  const [y, m, d] = String(isoStr).split("-").map(Number);
  return `${d} ${months[m - 1]} ${y}`;
}

/** Bugünün tarihini YYYY-MM-DD formatında döndürür */
function todayISO() {
  return new Date().toISOString().split("T")[0];
}

/** Leitner kutusu Türkçe etiketi */
function getLevelLabel(status) {
  const map = {
    Box1:     "📦 Kutu 1 — Yeni",
    Box2:     "📦 Kutu 2 — Öğreniliyor",
    Box3:     "📦 Kutu 3 — Pekiştiriliyor",
    Mastered: "✅ Tamamlandı",
  };
  return map[status] || status;
}

/** Leitner kutusuna göre CSS badge sınıfı */
function getBadgeClass(status) {
  const map = {
    Box1:     "badge-box1",
    Box2:     "badge-box2",
    Box3:     "badge-box3",
    Mastered: "badge-mastered",
  };
  return map[status] || "";
}

/** Kalan güne göre renk sınıfı (acil durum sistemi) */
function getDaysColor(days) {
  if (days <= 3) return "text-rose-400";
  if (days <= 7) return "text-amber-400";
  return "text-emerald-400";
}

/** Kullanıcı dostu hata mesajı */
function friendlyError(err) {
  if (!err) return "Bilinmeyen bir hata oluştu.";
  const msg = typeof err === "string" ? err : (err.message || String(err));
  if (msg.includes("Failed to fetch") || msg.includes("NetworkError"))
    return "Sunucuya bağlanılamadı. Sunucu çalışıyor mu?";
  if (msg.includes("401") || msg.includes("API key"))
    return "API anahtarı geçersiz veya eksik.";
  return msg;
}

/** Toast bildirim sistemi */
function showToast(message, type = "success") {
  const container = document.getElementById("toast-container");
  if (!container) return;

  const toast = document.createElement("div");
  const baseClasses = "px-4 py-3 rounded-xl border shadow-xl flex items-center justify-between gap-3 text-sm font-semibold toast-enter bg-slate-950/95 backdrop-blur-md transition-all duration-300";
  
  let typeClasses = "";
  let icon = "";
  if (type === "error") {
    typeClasses = "border-rose-500/30 text-rose-300 shadow-rose-950/20";
    icon = "⚠️";
  } else if (type === "warning") {
    typeClasses = "border-amber-500/30 text-amber-300 shadow-amber-950/20";
    icon = "🔔";
  } else {
    typeClasses = "border-emerald-500/30 text-emerald-300 shadow-emerald-950/20";
    icon = "✓";
  }

  toast.className = `${baseClasses} ${typeClasses}`;
  toast.innerHTML = `
    <div class="flex items-center gap-2.5">
      <span class="text-base">${icon}</span>
      <span>${escapeHtml(message)}</span>
    </div>
    <button class="text-slate-500 hover:text-slate-300 text-xs font-bold pl-2 active:scale-90" onclick="this.parentElement.remove()">✕</button>
  `;

  container.appendChild(toast);

  // 3.5 saniye sonra otomatik kaldır
  setTimeout(() => {
    if (toast.parentElement) {
      toast.classList.replace("toast-enter", "toast-exit");
      toast.addEventListener("animationend", () => {
        toast.remove();
      });
    }
  }, 3500);
}

// ─── Tarih Validasyonu (geçmiş tarih seçilemez) ─────────

(function setMinDate() {
  const dateInput = document.getElementById("exam-date");
  if (dateInput) {
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    dateInput.min = tomorrow.toISOString().split("T")[0];
  }
})();

// ─── SINAV İŞLEMLERİ ────────────────────────────────────

async function fetchExams() {
  const skeleton = document.getElementById("exams-skeleton");
  if (skeleton) skeleton.classList.remove("hidden");

  try {
    const response = await fetch(`${apiRoot}/exams`);
    if (!response.ok) throw new Error(`Sınavlar yüklenemedi (${response.status})`);
    const exams = await response.json();
    renderExamCards(exams);
  } catch (err) {
    if (examsList) {
      examsList.innerHTML = `
        <div class="rounded-xl bg-rose-500/10 border border-rose-500/20 p-4 text-center text-rose-400 text-sm">
          ⚠️ ${friendlyError(err)}
        </div>`;
    }
  } finally {
    if (skeleton) skeleton.classList.add("hidden");
  }
}

function renderExamCards(exams) {
  if (!examsList) return;

  if (!exams || exams.length === 0) {
    examsList.innerHTML = `
      <div class="flex flex-col items-center justify-center py-12 text-center fade-up">
        <p class="text-5xl mb-4">📝</p>
        <p class="text-slate-300 font-semibold">Henüz sınav eklenmedi</p>
        <p class="text-slate-500 text-sm mt-1">Soldaki formdan ilk sınavınızı oluşturun.</p>
      </div>`;
    return;
  }

  examsList.innerHTML = exams.map((exam) => {
    const isExpired = exam.remaining_days <= 0;
    const daysColor = getDaysColor(exam.remaining_days);
    const total    = exam.flashcard_count || 0;
    const mastered = exam.mastered_count  || 0;
    const pct      = total > 0 ? Math.round((mastered / total) * 100) : 0;

    const daysBadge = isExpired 
      ? `<span class="badge-expired text-[10px] font-bold px-2 py-0.5 rounded-md">⌛ Süre Doldu</span>` 
      : `<span class="${daysColor} text-sm font-bold">${exam.remaining_days} gün</span>`;

    return `
    <div class="flex items-stretch gap-2 group fade-up">
      <button class="flex-1 rounded-xl border border-slate-800 bg-slate-950/50 px-5 py-4 text-left
                     transition hover:border-emerald-500/50 hover:bg-slate-800/60 active:scale-[.99]"
        onclick="selectExam('${exam.exam_id}')">
        <div class="flex items-center justify-between">
          <span class="font-bold text-white text-sm">${escapeHtml(exam.course_name)}</span>
          ${daysBadge}
        </div>
        <p class="mt-1 text-xs text-slate-500">
          ${formatDateTR(exam.exam_date)} &middot; ${total} kart &middot; Hedef: ${exam.daily_target}/gün
        </p>
        ${total > 0 ? `
        <div class="mt-3">
          <div class="flex items-center justify-between text-[10px] text-slate-500 mb-1">
            <span>İlerleme</span>
            <span class="font-bold text-emerald-400">${pct}%</span>
          </div>
          <div class="h-1.5 w-full rounded-full bg-slate-800 overflow-hidden">
            <div class="progress-fill h-full rounded-full bg-emerald-400" style="width:${pct}%"></div>
          </div>
        </div>` : ""}
      </button>
      <button onclick="deleteExam('${exam.exam_id}')"
        class="flex items-center justify-center rounded-xl bg-rose-500/10 border border-rose-500/20
               px-3.5 text-rose-400 text-lg font-bold transition hover:bg-rose-500/20 hover:border-rose-400 active:scale-95"
        title="Sınavı Sil">✕</button>
    </div>`;
  }).join("");
}

window.deleteExam = async function (examId) {
  if (!confirm("Bu sınavı ve tüm flashcard'larını silmek istediğinize emin misiniz?\nBu işlem geri alınamaz!")) return;
  try {
    const resp = await fetch(`${apiRoot}/exams/${examId}`, { method: "DELETE" });
    if (!resp.ok) throw new Error("Silme işlemi başarısız.");
    
    showToast("Sınav ve ilişkili kartlar başarıyla silindi.", "success");

    if (currentExam && currentExam.exam_id === examId) {
      currentExam = null;
      detailsSection.classList.add("hidden");
    }
    await fetchExams();
  } catch (err) {
    showToast("Silme hatası: " + friendlyError(err), "error");
  }
};

window.selectExam = async function (examId) {
  try {
    const response = await fetch(`${apiRoot}/exams/${examId}`);
    if (!response.ok) throw new Error(`Sınav yüklenemedi (${response.status})`);
    const exam = await response.json();
    currentExam = exam;

    selectedExamEl.textContent = `${exam.course_name} — ${formatDateTR(exam.exam_date)}`;

    // Kalan gün renklendirmesi
    if (exam.remaining_days <= 0) {
      remainingDaysEl.innerHTML = `<span class="text-rose-400 text-lg font-extrabold uppercase">⌛ Süre Doldu</span>`;
    } else {
      remainingDaysEl.textContent = exam.remaining_days;
      remainingDaysEl.className = `mt-2 text-3xl font-extrabold ${getDaysColor(exam.remaining_days)}`;
    }

    if (dailyTargetEl)    dailyTargetEl.textContent    = exam.daily_target;
    if (totalCardsEl)     totalCardsEl.textContent     = exam.flashcard_count || 0;
    if (completedTodayEl) completedTodayEl.textContent = exam.mastered_count  || 0;

    detailsSection.classList.remove("hidden");
    
    // Smooth scroll to details
    detailsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });

    await loadFlashcards(examId);
    await fetchExams(); // sınav listesini de güncelle
  } catch (err) {
    showToast("Sınav detayları yüklenemedi: " + friendlyError(err), "error");
  }
};

// ─── FLASHCARD İŞLEMLERİ ────────────────────────────────

function updateStats(flashcards) {
  const box1     = flashcards.filter(c => c.status === "Box1").length;
  const learning = flashcards.filter(c => c.status === "Box2" || c.status === "Box3").length;
  const mastered = flashcards.filter(c => c.status === "Mastered").length;

  const el1 = document.getElementById("stat-box1");
  const el2 = document.getElementById("stat-learning");
  const el3 = document.getElementById("stat-mastered");
  if (el1) el1.textContent = box1;
  if (el2) el2.textContent = learning;
  if (el3) el3.textContent = mastered;
}

async function loadFlashcards(examId) {
  // Skeleton loading state
  flashcardsList.innerHTML = `
    <div class="space-y-4">
      <div class="skeleton h-[210px] w-full"></div>
      <div class="skeleton h-[210px] w-full"></div>
    </div>
  `;

  try {
    const response = await fetch(`${apiRoot}/exams/${examId}/flashcards`);
    if (!response.ok) throw new Error(`Flashcard'lar yüklenemedi (${response.status})`);
    const flashcards = await response.json();

    updateStats(flashcards);

    if (flashcards.length === 0) {
      flashcardsList.innerHTML = `
        <div class="flex flex-col items-center justify-center py-10 text-center fade-up">
          <p class="text-4xl mb-3">🃏</p>
          <p class="text-slate-300 font-semibold text-sm">Henüz flashcard yok</p>
          <p class="text-slate-500 text-xs mt-1">Formu veya Yapay Zekâ Asistanını kullanarak oluşturun.</p>
        </div>`;
      return;
    }

    flashcardsList.innerHTML = flashcards.map((card) => {
      const isMastered = card.status === "Mastered";

      return `
      <div class="card-container fade-up" style="min-height:210px;">
        <div class="flashcard rounded-2xl cursor-pointer" onclick="toggleCard(this)" style="min-height:210px;">

          <!-- ÖN YÜZ -->
          <div class="card-face bg-slate-950 border border-slate-800 flex flex-col">
            <div class="flex items-center justify-between mb-3">
              <span class="text-[10px] font-bold uppercase tracking-widest text-slate-600">Ön Yüz</span>
              <span class="rounded-full px-2.5 py-0.5 text-[10px] font-bold ${getBadgeClass(card.status)}">
                ${getLevelLabel(card.status)}
              </span>
            </div>
            <h3 class="flex-1 text-sm font-semibold leading-relaxed text-slate-100">${escapeHtml(card.front_side)}</h3>
            <p class="mt-4 text-[11px] text-slate-600 italic">Cevabı görmek için tıkla →</p>
          </div>

          <!-- ARKA YÜZ -->
          <div class="card-face card-back bg-slate-900 border border-slate-700 flex flex-col" onclick="event.stopPropagation()">
            <p class="text-[10px] font-bold uppercase tracking-widest text-slate-500 mb-3">Arka Yüz</p>
            <p class="flex-1 text-sm font-semibold leading-relaxed text-slate-100">${escapeHtml(card.back_side)}</p>
            <div class="flex gap-2 pt-4 border-t border-slate-800 mt-4">
              ${!isMastered ? `
                <button class="flex-1 rounded-lg bg-emerald-500 py-2 text-xs font-bold text-slate-950
                               transition hover:bg-emerald-400 active:scale-95"
                  onclick="markKnown('${card.card_id}')">✓ Bildim</button>
              ` : ""}
              <button class="flex-1 rounded-lg bg-rose-500 py-2 text-xs font-bold text-white
                             transition hover:bg-rose-400 active:scale-95"
                onclick="markUnknown('${card.card_id}')">✗ Bilemedim</button>
              <button class="rounded-lg bg-slate-700 px-3 py-2 text-xs text-slate-300
                             transition hover:bg-slate-600 active:scale-95"
                onclick="deleteCard('${card.card_id}')" title="Kartı Sil">🗑</button>
            </div>
          </div>

        </div>
      </div>`;
    }).join("");
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

window.markKnown    = (cardId) => updateLeitner(cardId, true);
window.markUnknown  = (cardId) => updateLeitner(cardId, false);
window.deleteCard   = deleteCardFn;

async function updateLeitner(cardId, known) {
  try {
    const resp = await fetch(`${apiRoot}/flashcards/${cardId}/leitner`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ known }),
    });
    if (!resp.ok) {
      const data = await resp.json().catch(() => null);
      throw new Error(data?.detail || "Güncelleme başarısız.");
    }
    
    showToast(known ? "Harika! Kart bir sonraki kutuya yükseldi." : "Kart Kutu 1'e geri alındı.", known ? "success" : "warning");

    if (currentExam) await selectExam(currentExam.exam_id);
  } catch (err) {
    showToast("Güncelleme hatası: " + friendlyError(err), "error");
  }
}

async function deleteCardFn(cardId) {
  if (!confirm("Bu kartı kalıcı olarak silmek istediğinize emin misiniz?")) return;
  try {
    const resp = await fetch(`${apiRoot}/flashcards/${cardId}`, { method: "DELETE" });
    if (!resp.ok) throw new Error("Silme başarısız.");
    
    showToast("Flashcard başarıyla silindi.", "success");

    if (currentExam) await selectExam(currentExam.exam_id);
  } catch (err) {
    showToast("Kart silme hatası: " + friendlyError(err), "error");
  }
}

// ─── FORM EVENT'LERİ ────────────────────────────────────

if (examForm) {
  examForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const courseName = document.getElementById("exam-course").value.trim();
    const examDate   = document.getElementById("exam-date").value;

    if (!courseName || !examDate) return;

    // İstemci tarafında tarih doğrulaması
    if (examDate <= todayISO()) {
      showToast("Sınav tarihi bugünden ileri bir tarih olmalıdır.", "error");
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
      showToast("Sınav başarıyla oluşturuldu!", "success");
      await fetchExams();
    } catch (err) {
      showToast("Sınav oluşturma hatası: " + friendlyError(err), "error");
    }
  });
}

if (flashcardForm) {
  flashcardForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    if (!currentExam) {
      showToast("Lütfen önce bir sınav seçin.", "warning");
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
      showToast("Flashcard başarıyla eklendi!", "success");
      await selectExam(currentExam.exam_id);
    } catch (err) {
      showToast("Kart oluşturma hatası: " + friendlyError(err), "error");
    }
  });
}

// ─── AI KART ÜRETİMİ ────────────────────────────────────

if (aiBtn) {
  aiBtn.addEventListener("click", async () => {
    if (!currentExam) {
      showToast("Lütfen önce bir sınav seçin.", "warning");
      return;
    }
    aiBtn.disabled = true;
    const prev = aiBtn.innerHTML;
    aiBtn.innerHTML = '<span class="animate-pulse">⏳ Yapay zekâ düşünüyor…</span>';

    try {
      const resp = await fetch(`${apiRoot}/exams/${currentExam.exam_id}/generate-ai-cards`, {
        method: "POST",
      });
      if (!resp.ok) {
        const data = await resp.json().catch(() => null);
        throw new Error(data?.detail || "Yapay zekâ kart üretimi başarısız.");
      }
      
      showToast("Yapay zekâ başarıyla 3 yeni soru üretti!", "success");
      await selectExam(currentExam.exam_id);
    } catch (err) {
      showToast(friendlyError(err), "error");
    } finally {
      aiBtn.disabled = false;
      aiBtn.innerHTML = prev;
    }
  });
}

// ─── BAŞLANGIÇ ───────────────────────────────────────────
fetchExams();
