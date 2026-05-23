"""AI servis birim testleri — demo modu, JSON parse, hata yönetimi."""

import json
from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio

import pytest

from app.services.ai_service import generate_flashcards_raw


@pytest.mark.asyncio
async def test_demo_mode_returns_sample_cards() -> None:
    """DEMO_MODE aktifken yerel örnek kartlar dönmeli."""
    with patch("app.services.ai_service.DEMO_MODE", True):
        result = await generate_flashcards_raw("Veri Yapıları")
    assert len(result) == 3
    assert all("soru" in card and "cevap" in card for card in result)
    assert result[0]["soru"].startswith("Demo:")


@pytest.mark.asyncio
async def test_empty_api_key_returns_demo() -> None:
    """API anahtarı boşken demo modu aktifleşmeli."""
    with patch("app.services.ai_service.GROQ_API_KEY", ""), \
         patch("app.services.ai_service.DEMO_MODE", False):
        result = await generate_flashcards_raw("Matematik")
    assert len(result) == 3
    assert result[0]["soru"].startswith("Demo:")


@pytest.mark.asyncio
async def test_parse_json_array_response() -> None:
    """Doğrudan JSON dizisi dönen yanıt başarıyla parse edilmeli."""
    mock_response = json.dumps([
        {"soru": "Test soru 1", "cevap": "Test cevap 1"},
        {"soru": "Test soru 2", "cevap": "Test cevap 2"},
    ])
    with patch("app.services.ai_service.DEMO_MODE", False), \
         patch("app.services.ai_service.GROQ_API_KEY", "test-key"), \
         patch("app.services.ai_service.asyncio") as mock_asyncio:
        mock_asyncio.to_thread = AsyncMock(return_value=mock_response)
        result = await generate_flashcards_raw("Test Dersi")
    assert len(result) == 2
    assert result[0]["soru"] == "Test soru 1"


@pytest.mark.asyncio
async def test_parse_json_object_wrapping_array() -> None:
    """JSON objesi içinde sarılı dizi başarıyla çıkarılmalı."""
    mock_response = json.dumps({
        "sorular": [
            {"soru": "Wrapped soru", "cevap": "Wrapped cevap"},
        ]
    })
    with patch("app.services.ai_service.DEMO_MODE", False), \
         patch("app.services.ai_service.GROQ_API_KEY", "test-key"), \
         patch("app.services.ai_service.asyncio") as mock_asyncio:
        mock_asyncio.to_thread = AsyncMock(return_value=mock_response)
        result = await generate_flashcards_raw("Test")
    assert len(result) == 1
    assert result[0]["soru"] == "Wrapped soru"


@pytest.mark.asyncio
async def test_api_error_raises_value_error() -> None:
    """API hatası ValueError fırlatmalı."""
    with patch("app.services.ai_service.DEMO_MODE", False), \
         patch("app.services.ai_service.GROQ_API_KEY", "test-key"), \
         patch("app.services.ai_service.asyncio") as mock_asyncio:
        mock_asyncio.to_thread = AsyncMock(side_effect=ConnectionError("API down"))
        with pytest.raises(ValueError, match="Yapay zekâ servisi"):
            await generate_flashcards_raw("Test")


@pytest.mark.asyncio
async def test_invalid_json_raises_value_error() -> None:
    """Geçersiz JSON yanıtı ValueError fırlatmalı."""
    with patch("app.services.ai_service.DEMO_MODE", False), \
         patch("app.services.ai_service.GROQ_API_KEY", "test-key"), \
         patch("app.services.ai_service.asyncio") as mock_asyncio:
        mock_asyncio.to_thread = AsyncMock(return_value="this is not json at all")
        with pytest.raises(ValueError, match="işlenemedi"):
            await generate_flashcards_raw("Test")


@pytest.mark.asyncio
async def test_empty_list_raises_value_error() -> None:
    """Boş liste dönen yanıt ValueError fırlatmalı."""
    with patch("app.services.ai_service.DEMO_MODE", False), \
         patch("app.services.ai_service.GROQ_API_KEY", "test-key"), \
         patch("app.services.ai_service.asyncio") as mock_asyncio:
        mock_asyncio.to_thread = AsyncMock(return_value="[]")
        with pytest.raises(ValueError, match="soru üretemedi"):
            await generate_flashcards_raw("Test")


@pytest.mark.asyncio
async def test_normalizes_alternative_field_names() -> None:
    """'question'/'answer' alan isimleri 'soru'/'cevap' olarak normalize edilmeli."""
    mock_response = json.dumps([
        {"question": "English question", "answer": "English answer"},
    ])
    with patch("app.services.ai_service.DEMO_MODE", False), \
         patch("app.services.ai_service.GROQ_API_KEY", "test-key"), \
         patch("app.services.ai_service.asyncio") as mock_asyncio:
        mock_asyncio.to_thread = AsyncMock(return_value=mock_response)
        result = await generate_flashcards_raw("Test")
    assert len(result) == 1
    assert result[0]["soru"] == "English question"
    assert result[0]["cevap"] == "English answer"


@pytest.mark.asyncio
async def test_skips_items_with_missing_fields() -> None:
    """Eksik alanları olan öğeler atlanmalı."""
    mock_response = json.dumps([
        {"soru": "Valid soru", "cevap": "Valid cevap"},
        {"soru": "Only question"},  # cevap yok
        {"cevap": "Only answer"},   # soru yok
    ])
    with patch("app.services.ai_service.DEMO_MODE", False), \
         patch("app.services.ai_service.GROQ_API_KEY", "test-key"), \
         patch("app.services.ai_service.asyncio") as mock_asyncio:
        mock_asyncio.to_thread = AsyncMock(return_value=mock_response)
        result = await generate_flashcards_raw("Test")
    assert len(result) == 1
    assert result[0]["soru"] == "Valid soru"
