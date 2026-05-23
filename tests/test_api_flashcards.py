"""Flashcard API endpoint'leri integration testleri."""

from datetime import date, timedelta

from fastapi.testclient import TestClient


def _future_date(days: int = 10) -> str:
    return (date.today() + timedelta(days=days)).isoformat()


def _create_exam(client: TestClient) -> str:
    """Yardımcı: Test için sınav oluşturur, exam_id döner."""
    resp = client.post("/api/exams/", json={
        "course_name": "Test Dersi",
        "exam_date": _future_date(),
    })
    return resp.json()["exam_id"]


def test_create_flashcard_success(client: TestClient) -> None:
    """Geçerli verilerle flashcard oluşturulabilmeli."""
    exam_id = _create_exam(client)
    resp = client.post("/api/flashcards/", json={
        "exam_id": exam_id,
        "front_side": "CPU nedir?",
        "back_side": "Merkezi işlem birimidir.",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["front_side"] == "CPU nedir?"
    assert data["status"] == "Box1"


def test_create_flashcard_invalid_exam(client: TestClient) -> None:
    """Olmayan sınav ID'siyle flashcard oluşturma 404 dönmeli."""
    resp = client.post("/api/flashcards/", json={
        "exam_id": "nonexistent-id",
        "front_side": "Soru",
        "back_side": "Cevap",
    })
    assert resp.status_code == 404


def test_create_flashcard_empty_front(client: TestClient) -> None:
    """Boş ön yüzle flashcard oluşturma reddedilmeli."""
    exam_id = _create_exam(client)
    resp = client.post("/api/flashcards/", json={
        "exam_id": exam_id,
        "front_side": "",
        "back_side": "Cevap",
    })
    assert resp.status_code == 422


def test_create_flashcard_empty_back(client: TestClient) -> None:
    """Boş arka yüzle flashcard oluşturma reddedilmeli."""
    exam_id = _create_exam(client)
    resp = client.post("/api/flashcards/", json={
        "exam_id": exam_id,
        "front_side": "Soru",
        "back_side": "",
    })
    assert resp.status_code == 422


def test_leitner_known_promotes_to_box2(client: TestClient) -> None:
    """Bildim ile Box1 → Box2 geçişi olmalı."""
    exam_id = _create_exam(client)
    card_resp = client.post("/api/flashcards/", json={
        "exam_id": exam_id,
        "front_side": "Soru A",
        "back_side": "Cevap A",
    })
    card_id = card_resp.json()["card_id"]

    resp = client.patch(f"/api/flashcards/{card_id}/leitner", json={"known": True})
    assert resp.status_code == 200
    assert resp.json()["status"] == "Box2"


def test_leitner_full_progression(client: TestClient) -> None:
    """Box1 → Box2 → Box3 → Mastered tam geçiş testi."""
    exam_id = _create_exam(client)
    card_resp = client.post("/api/flashcards/", json={
        "exam_id": exam_id,
        "front_side": "Soru B",
        "back_side": "Cevap B",
    })
    card_id = card_resp.json()["card_id"]

    # Box1 → Box2
    resp = client.patch(f"/api/flashcards/{card_id}/leitner", json={"known": True})
    assert resp.json()["status"] == "Box2"
    # Box2 → Box3
    resp = client.patch(f"/api/flashcards/{card_id}/leitner", json={"known": True})
    assert resp.json()["status"] == "Box3"
    # Box3 → Mastered
    resp = client.patch(f"/api/flashcards/{card_id}/leitner", json={"known": True})
    assert resp.json()["status"] == "Mastered"


def test_leitner_unknown_resets_to_box1(client: TestClient) -> None:
    """Bilemedim ile herhangi bir kutudan Box1'e dönmeli."""
    exam_id = _create_exam(client)
    card_resp = client.post("/api/flashcards/", json={
        "exam_id": exam_id,
        "front_side": "Soru C",
        "back_side": "Cevap C",
    })
    card_id = card_resp.json()["card_id"]

    # Box1 → Box2
    client.patch(f"/api/flashcards/{card_id}/leitner", json={"known": True})
    # Box2 → Box1 (Bilemedim)
    resp = client.patch(f"/api/flashcards/{card_id}/leitner", json={"known": False})
    assert resp.json()["status"] == "Box1"


def test_leitner_card_not_found(client: TestClient) -> None:
    """Olmayan kart ID'siyle Leitner güncellemesi 404 dönmeli."""
    resp = client.patch("/api/flashcards/nonexistent/leitner", json={"known": True})
    assert resp.status_code == 404


def test_delete_flashcard(client: TestClient) -> None:
    """Flashcard silinebilmeli."""
    exam_id = _create_exam(client)
    card_resp = client.post("/api/flashcards/", json={
        "exam_id": exam_id,
        "front_side": "Soru D",
        "back_side": "Cevap D",
    })
    card_id = card_resp.json()["card_id"]

    del_resp = client.delete(f"/api/flashcards/{card_id}")
    assert del_resp.status_code == 204


def test_delete_flashcard_not_found(client: TestClient) -> None:
    """Olmayan flashcard silme 404 dönmeli."""
    resp = client.delete("/api/flashcards/nonexistent-id")
    assert resp.status_code == 404


def test_cascade_delete_removes_flashcards(client: TestClient) -> None:
    """Sınav silindiğinde flashcard'lar da silinmeli."""
    exam_id = _create_exam(client)
    client.post("/api/flashcards/", json={
        "exam_id": exam_id,
        "front_side": "Soru E",
        "back_side": "Cevap E",
    })

    # Sınavı sil
    client.delete(f"/api/exams/{exam_id}")

    # Kartlar listelenemez (sınav yok)
    resp = client.get(f"/api/exams/{exam_id}/flashcards")
    assert resp.status_code == 404
