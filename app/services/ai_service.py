from __future__ import annotations
import os
import json
import re
import asyncio
from typing import List, Dict
from dotenv import load_dotenv

# .env dosyasını oku
load_dotenv()

# Ortam değişkenlerini çek — .env'de GROQ_API_KEY tanımlı
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() == "true"


def _call_groq_sync(course_name: str) -> str:
    """Senkron Groq API çağrısı — asyncio.to_thread içinde çalışır."""
    from groq import Groq
    client = Groq(api_key=GROQ_API_KEY)

    system_prompt = (
        "Sen bir üniversite akademisyenisin. Verilen ders adıyla ilgili, flashcard mantığına uygun "
        "(kısa soru ve net cevap) 3 adet popüler teknik soru-cevap çifti üret. "
        "Yanıtı ekstra hiçbir markdown işareti veya açıklama eklemeden SADECE şu saf JSON formatında döndür: "
        '[{"soru": "...", "cevap": "..."}]'
    )

    response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Ders: {course_name}"},
        ],
        model="llama-3.3-70b-versatile",
        temperature=0.3,
        max_tokens=512,
        response_format={"type": "json_object"},
    )
    return response.choices[0].message.content or ""


async def generate_flashcards_raw(course_name: str) -> List[Dict[str, str]]:
    """FastAPI event loop'unu bloklamadan Groq üzerinden flashcard üretir."""

    # Demo modu aktifse veya API anahtarı yoksa örnek veri dön
    if DEMO_MODE or not GROQ_API_KEY:
        return [
            {"soru": "Demo: Bağlı liste nedir?", "cevap": "Elemanların düğümler halinde birbirine bağlandığı yapıdır."},
            {"soru": "Demo: Stack hangi prensiple çalışır?", "cevap": "LIFO (Son giren ilk çıkar) prensibiyle çalışır."},
            {"soru": "Demo: Queue hangi prensiple çalışır?", "cevap": "FIFO (İlk giren ilk çıkar) prensibiyle çalışır."},
        ]

    try:
        # Senkron API çağrısını ayrı bir thread'de çalıştır — event loop'u bloklamaz
        text = await asyncio.to_thread(_call_groq_sync, course_name)
    except Exception as exc:
        raise ValueError(f"Yapay zekâ servisi şu anda yanıt veremiyor. Lütfen tekrar deneyin. (Detay: {exc})")

    # Regex ile JSON dizisini ayıkla (model bazen obje içinde döndürebilir)
    match = re.search(r"(\[\s*\{.*\}\s*\])", text, flags=re.DOTALL)
    if match:
        candidate = match.group(1)
    else:
        # json_object modunda { } ile sarılı gelebilir, içindeki listeyi bul
        try:
            parsed = json.loads(text)
            if isinstance(parsed, dict):
                for v in parsed.values():
                    if isinstance(v, list):
                        candidate = json.dumps(v)
                        break
                else:
                    candidate = text
            else:
                candidate = text
        except Exception:
            candidate = text

    try:
        data = json.loads(candidate)
    except Exception as exc:
        raise ValueError(f"Yapay zekâ yanıtı işlenemedi. Lütfen tekrar deneyin.")

    if not isinstance(data, list) or len(data) == 0:
        raise ValueError("Yapay zekâ bu ders için soru üretemedi. Lütfen farklı bir ders adı deneyin.")

    # Alanları normalize et
    results: List[Dict[str, str]] = []
    for item in data:
        if not isinstance(item, dict):
            continue
        soru = item.get("soru") or item.get("question") or item.get("front")
        cevap = item.get("cevap") or item.get("answer") or item.get("back")
        if not soru or not cevap:
            continue
        results.append({"soru": str(soru).strip(), "cevap": str(cevap).strip()})

    if not results:
        raise ValueError("Yapay zekâ yanıtından geçerli soru-cevap çifti çıkarılamadı. Lütfen tekrar deneyin.")

    return results