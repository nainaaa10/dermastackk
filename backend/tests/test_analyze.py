"""
Tests for Skin Image Analysis Endpoints.
"""

import io
import pytest
from PIL import Image
from httpx import AsyncClient, ASGITransport
from backend.app.main import app


def create_test_image_bytes(format="JPEG", size=(256, 256), color=(200, 150, 130)) -> bytes:
    """Creates an in-memory valid image buffer."""
    img = Image.new("RGB", size, color=color)
    buffer = io.BytesIO()
    img.save(buffer, format=format)
    return buffer.getvalue()


@pytest.mark.asyncio
async def test_analyze_valid_jpeg():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        img_bytes = create_test_image_bytes(format="JPEG")
        files = {
            "image": ("test_skin.jpg", img_bytes, "image/jpeg")
        }
        data = {
            "age_range": "30-45",
            "skin_type": "Fitzpatrick II",
            "concerns": "Mild redness and texture",
            "consent_to_save": "true"
        }
        response = await client.post("/api/v1/analyze", files=files, data=data)
        assert response.status_code == 200
        res = response.json()
        assert "report_id" in res
        assert res["report_id"].startswith("rpt_")
        assert res["inference_mode"] in ["demo_simulated", "trained_inference"]
        assert len(res["predictions"]) == 7
        assert "confidence_score" in res
        assert res["confidence_score"] >= 0.0
        assert "disclaimer" in res
        assert "educational_summary" in res
        assert res["is_persisted"] is True


@pytest.mark.asyncio
async def test_analyze_empty_file_rejected():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        files = {
            "image": ("empty.jpg", b"", "image/jpeg")
        }
        response = await client.post("/api/v1/analyze", files=files)
        assert response.status_code == 400
        assert "empty" in response.json()["message"].lower()


@pytest.mark.asyncio
async def test_analyze_unsupported_media_type():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        files = {
            "image": ("document.pdf", b"%PDF-1.4...", "application/pdf")
        }
        response = await client.post("/api/v1/analyze", files=files)
        assert response.status_code == 415


@pytest.mark.asyncio
async def test_analyze_corrupt_image_bytes():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        files = {
            "image": ("corrupted.jpg", b"NOT_AN_IMAGE_RANDOM_BYTES", "image/jpeg")
        }
        response = await client.post("/api/v1/analyze", files=files)
        assert response.status_code == 400
        assert "invalid or corrupted" in response.json()["message"].lower()
