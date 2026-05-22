from __future__ import annotations
import os
import json
import re
from typing import List, Dict
from dotenv import load_dotenv
from google import generativeai as gaia

# .env dosyasını oku
load_dotenv()

# Ortam değişkenlerini çek
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() == "true"

async def generate_flashcards_raw(course_name: str) -> List[Dict[str, str]]:
    # Demo modu aktifse veya anahtar yoksa test soruları dön (çökme olmasın)
    if DEMO_MODE or not GOOGLE_API_KEY:
        return [
            {"soru": "Demo: Bağlı liste nedir?", "cevap": "Elemanların düğümler halinde birbirine bağlandığı yapıdır."},
            {"soru": "Demo: Stack hangi prensiple çalışır?", "cevap": "LIFO (Son giren ilk çıkar) prensibiyle çalışır."}
        ]

    # Gerçek API yapılandırması
    gaia.configure(api_key=GOOGLE_API_KEY)

    system_prompt = (
        "Sen bir üniversite akademisyenisin. Verilen ders adıyla ilgili, flashcard mantığına uygun "
        "(kısa soru ve net cevap) 3 adet popüler teknik soru-cevap çifti üret. "
        "Yanıtı ekstra hiçbir markdown işareti veya açıklama eklemeden SADECE şu saf JSON formatında döndür: "
        "[{'soru': '...', 'cevap': '...'}]"
    )

    prompt = f"{system_prompt}\nDers: {course_name}"

    # Gemini 1.5 Flash modelini JSON çıktısı vermeye zorlayarak tanımla
    model = gaia.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config={
            "temperature": 0.3,
            "max_output_tokens": 512,
            "response_mime_type": "application/json"
        }
    )

    # İstatistiksel olarak asenkron üretimi tetikle
    response = model.generate_content(prompt)
    text = response.text.strip() if hasattr(response, "text") else str(response)

    # Markdown blokları varsa temizle
    if text.startswith("```"):
        text = text.strip("`").replace("json", "", 1).strip()

    # Regex ile JSON dizisini ayıkla
    match = re.search(r"(\[\s*\{.*\}\s*\])", text, flags=re.DOTALL)
    candidate = match.group(1) if match else text

    try:
        data = json.loads(candidate)
    except Exception as exc:
        raise ValueError(f"AI yanıtı JSON parse edilemedi: {exc}\nRaw: {text}")

    # Alanları normalize et
    results: List[Dict[str, str]] = []
    for item in data:
        soru = item.get("soru") or item.get("question") or item.get("front")
        cevap = item.get("cevap") or item.get("answer") or item.get("back")
        if not soru or not cevap:
            continue
        results.append({"soru": str(soru).strip(), "cevap": str(cevap).strip()})

    return results