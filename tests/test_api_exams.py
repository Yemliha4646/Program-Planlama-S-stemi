"""Sınav API endpoint'leri integration testleri."""

from datetime import date, timedelta

from fastapi.testclient import TestClient


def _future_date(days: int = 10) -> str:
    return (date.today() + timedelta(days=days)).isoformat()


def _past_date() -> str:
    return (date.today() - timedelta(days=1)).isoformat()


def test_create_exam_success(client: TestClient) -> None:
    """Geçerli verilerle sınav oluşturulabilmeli."""
    resp = client.post("/api/exams/", json={
        "course_name": "Veri Yapıları",
        "exam_date": _future_date(15),
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["course_name"] == "Veri Yapıları"
    assert data["remaining_days"] > 0
    assert len(data["exam_id"]) == 36


def test_create_exam_rejects_past_date(client: TestClient) -> None:
    """Geçmiş tarihli sınav oluşturma reddedilmeli."""
    resp = client.post("/api/exams/", json={
        "course_name": "Matematik",
        "exam_date": _past_date(),
    })
    assert resp.status_code == 422


def test_create_exam_rejects_empty_name(client: TestClient) -> None:
    """Boş ders adıyla sınav oluşturma reddedilmeli."""
    resp = client.post("/api/exams/", json={
        "course_name": "",
        "exam_date": _future_date(),
    })
    assert resp.status_code == 422


def test_list_exams_empty(client: TestClient) -> None:
    """Boş veritabanında sınav listesi boş dönmeli."""
    resp = client.get("/api/exams/")
    assert resp.status_code == 200
    assert resp.json() == []


def test_list_exams_returns_created(client: TestClient) -> None:
    """Oluşturulan sınavlar listede görünmeli."""
    client.post("/api/exams/", json={
        "course_name": "Fizik",
        "exam_date": _future_date(),
    })
    resp = client.get("/api/exams/")
    assert resp.status_code == 200
    exams = resp.json()
    assert len(exams) == 1
    assert exams[0]["course_name"] == "Fizik"


def test_get_exam_by_id(client: TestClient) -> None:
    """ID ile sınav detayı alınabilmeli."""
    create_resp = client.post("/api/exams/", json={
        "course_name": "Kimya",
        "exam_date": _future_date(),
    })
    exam_id = create_resp.json()["exam_id"]
    resp = client.get(f"/api/exams/{exam_id}")
    assert resp.status_code == 200
    assert resp.json()["exam_id"] == exam_id


def test_get_exam_not_found(client: TestClient) -> None:
    """Olmayan sınav ID'si 404 dönmeli."""
    resp = client.get("/api/exams/nonexistent-id")
    assert resp.status_code == 404


def test_update_exam_date(client: TestClient) -> None:
    """Sınav tarihi güncellenebilmeli."""
    create_resp = client.post("/api/exams/", json={
        "course_name": "Biyoloji",
        "exam_date": _future_date(10),
    })
    exam_id = create_resp.json()["exam_id"]
    new_date = _future_date(20)
    resp = client.patch(f"/api/exams/{exam_id}", json={"exam_date": new_date})
    assert resp.status_code == 200
    assert resp.json()["exam_date"] == new_date


def test_update_exam_rejects_past_date(client: TestClient) -> None:
    """Geçmiş tarihle güncelleme reddedilmeli."""
    create_resp = client.post("/api/exams/", json={
        "course_name": "Tarih",
        "exam_date": _future_date(),
    })
    exam_id = create_resp.json()["exam_id"]
    resp = client.patch(f"/api/exams/{exam_id}", json={"exam_date": _past_date()})
    assert resp.status_code == 422


def test_delete_exam(client: TestClient) -> None:
    """Sınav silinebilmeli ve tekrar erişilemez olmalı."""
    create_resp = client.post("/api/exams/", json={
        "course_name": "Edebiyat",
        "exam_date": _future_date(),
    })
    exam_id = create_resp.json()["exam_id"]
    del_resp = client.delete(f"/api/exams/{exam_id}")
    assert del_resp.status_code == 200
    get_resp = client.get(f"/api/exams/{exam_id}")
    assert get_resp.status_code == 404


def test_delete_exam_not_found(client: TestClient) -> None:
    """Olmayan sınav silme 404 dönmeli."""
    resp = client.delete("/api/exams/nonexistent-id")
    assert resp.status_code == 404


def test_list_exam_flashcards_empty(client: TestClient) -> None:
    """Yeni sınavın kart listesi boş dönmeli."""
    create_resp = client.post("/api/exams/", json={
        "course_name": "Felsefe",
        "exam_date": _future_date(),
    })
    exam_id = create_resp.json()["exam_id"]
    resp = client.get(f"/api/exams/{exam_id}/flashcards")
    assert resp.status_code == 200
    assert resp.json() == []


def test_exam_response_includes_flashcard_count(client: TestClient) -> None:
    """Sınava kart eklendiğinde flashcard_count güncellenmeli."""
    create_resp = client.post("/api/exams/", json={
        "course_name": "Coğrafya",
        "exam_date": _future_date(),
    })
    exam_id = create_resp.json()["exam_id"]

    # Kart ekle
    client.post("/api/flashcards/", json={
        "exam_id": exam_id,
        "front_side": "Dünya'nın en uzun nehri?",
        "back_side": "Nil Nehri",
    })

    resp = client.get(f"/api/exams/{exam_id}")
    assert resp.status_code == 200
    assert resp.json()["flashcard_count"] == 1
