from __future__ import annotations
import os
import json
import re
from typing import List, Dict
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() == "true"

async def generate_flashcards_raw(course_name: str) -> List[Dict[str, str]]:
    if DEMO_MODE or not GROQ_API_KEY:
        return [
            {"soru": "Demo: Bağlı liste nedir?", "cevap": "Elemanların düğümler halinde birbirine bağlandığı yapıdır."},
            {"soru": "Demo: Stack hangi prensiple çalışır?", "cevap": "LIFO (Son giren ilk çıkar) prensibiyle çalışır."}
        ]

    client = Groq(api_key=GROQ_API_KEY)

    prompt = (
        f"Sen bir üniversite akademisyenisin. '{course_name}' dersiyle ilgili "
        "flashcard mantığına uygun 3 adet soru-cevap çifti üret. "
        "SADECE şu JSON formatında döndür, başka hiçbir şey yazma: "
        '[{"soru": "...", "cevap": "..."}]'
    )

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=512,
    )

    text = response.choices[0].message.content.strip()

    if text.startswith("```"):
        text = re.sub(r"```[a-z]*", "", text).replace("```", "").strip()

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