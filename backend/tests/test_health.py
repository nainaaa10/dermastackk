"""
Tests for Health and Status API Endpoints.
"""

import pytest
from httpx import AsyncClient, ASGITransport
from backend.app.main import app


@pytest.mark.asyncio
async def test_root_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "online"
        assert "version" in data
        assert data["docs"] == "/docs"


@pytest.mark.asyncio
async def test_health_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "database_connected" in data
        assert "database_type" in data
        assert data["database_type"] in ["mongodb", "in_memory_demo"]
        assert "inference_mode" in data
        assert data["inference_mode"] in ["trained_model", "demo_mode", "demo_simulated", "trained_inference"]
        assert "weights_loaded" in data
