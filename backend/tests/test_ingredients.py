"""
Tests for Cosmetic Ingredient Analysis Endpoint.
"""

import pytest
from httpx import AsyncClient, ASGITransport
from backend.app.main import app


@pytest.mark.asyncio
async def test_check_known_ingredients():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "ingredient_text": "Water, Glycerin, Niacinamide, Hyaluronic Acid, Ceramides",
            "skin_concerns": ["dryness"],
            "known_sensitivities": []
        }
        response = await client.post("/api/v1/ingredients/check", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["total_identified"] >= 4
        assert data["total_unknown"] == 0
        assert "educational_overview" in data
        assert "disclaimer" in data


@pytest.mark.asyncio
async def test_check_unknown_ingredient():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "ingredient_text": "Water, SyntheticPolymerXYZ999, Glycerin",
            "skin_concerns": [],
            "known_sensitivities": []
        }
        response = await client.post("/api/v1/ingredients/check", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["total_unknown"] == 1
        assert "SyntheticPolymerXYZ999" in data["unknown_ingredients"]


@pytest.mark.asyncio
async def test_check_sensitivity_flagging():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "ingredient_text": "Water, Glycerin, Fragrance / Parfum, Alcohol Denat",
            "skin_concerns": ["rosacea", "barrier_damage"],
            "known_sensitivities": ["fragrance"]
        }
        response = await client.post("/api/v1/ingredients/check", json=payload)
        assert response.status_code == 200
        data = response.json()
        flags = " ".join(data["potential_flags"]).lower()
        assert "fragrance" in flags
        assert "irritation" in flags or "barrier" in flags


@pytest.mark.asyncio
async def test_check_empty_payload_rejected():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "ingredient_text": "   "
        }
        response = await client.post("/api/v1/ingredients/check", json=payload)
        assert response.status_code == 400
