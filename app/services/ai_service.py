from __future__ import annotations
import asyncio
import os
import json
import re
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() == "true"


def _build_client():
    """Groq client'ını oluşturur."""
    from groq import Groq
    return Groq(api_key=GROQ_API_KEY)


def _call_groq_sync(course_name: str) -> str:
    """Senkron Groq API çağrısı yapar ve ham yanıt metnini döndürür."""
    client = _build_client()

    prompt = (
        f"Sen bir üniversite akademisyenisin. '{course_name}' dersiyle ilgili "
        "flashcard mantığına uygun 3 adet soru-cevap çifti üret. "
        "SADECE şu JSON formatında döndür, başka hiçbir şey yazma: "
        '[{"soru": "...", "cevap": "..."}]'
    )

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=512,
    )

    return response.choices[0].message.content.strip()


def _parse_ai_response(text: str) -> List[Dict[str, str]]:
    """AI yanıtını JSON olarak parse eder."""
    # Markdown kod bloğu varsa temizle
    if text.startswith("```"):
        text = re.sub(r"```[a-z]*", "", text).replace("```", "").strip()

    # JSON dizisini bul
    match = re.search(r"(\[\s*\{.*\}\s*\])", text, flags=re.DOTALL)
    candidate = match.group(1) if match else text

    try:
        data = json.loads(candidate)
    except Exception as exc:
        raise ValueError(f"AI yanıtı JSON parse edilemedi: {exc}\nRaw: {text}")

    results: List[Dict[str, str]] = []
    for item in data:
        soru = item.get("soru") or item.get("question") or item.get("front")
        cevap = item.get("cevap") or item.get("answer") or item.get("back")
        if not soru or not cevap:
            continue
        results.append({"soru": str(soru).strip(), "cevap": str(cevap).strip()})

    return results


async def generate_flashcards_raw(course_name: str) -> List[Dict[str, str]]:
    """AI ile flashcard üretir. API key yoksa demo modda çalışır."""
    if DEMO_MODE or not GROQ_API_KEY:
        return [
            {"soru": "Demo: Bağlı liste nedir?", "cevap": "Elemanların düğümler halinde birbirine bağlandığı yapıdır."},
            {"soru": "Demo: Stack hangi prensiple çalışır?", "cevap": "LIFO (Son giren ilk çıkar) prensibiyle çalışır."}
        ]

    # Senkron Groq SDK çağrısını ayrı thread'de çalıştır
    # böylece async event loop bloklanmaz
    text = await asyncio.to_thread(_call_groq_sync, course_name)
    return _parse_ai_response(text)