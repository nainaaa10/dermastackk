"""
Tests for Report Retrieval and Listing Endpoints.
"""

import pytest
from httpx import AsyncClient, ASGITransport
from backend.app.main import app
from backend.tests.test_analyze import create_test_image_bytes


@pytest.mark.asyncio
async def test_report_lifecycle():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Post an analysis with consent_to_save
        img_bytes = create_test_image_bytes()
        files = {"image": ("skin.jpg", img_bytes, "image/jpeg")}
        data = {"consent_to_save": "true"}
        analyze_res = await client.post("/api/v1/analyze", files=files, data=data)
        assert analyze_res.status_code == 200
        report_id = analyze_res.json()["report_id"]

        # 2. Retrieve report by ID
        get_res = await client.get(f"/api/v1/reports/{report_id}")
        assert get_res.status_code == 200
        report = get_res.json()
        assert report["report_id"] == report_id
        assert "predictions" in report
        assert len(report["predictions"]) == 7

        # 3. List reports
        list_res = await client.get("/api/v1/reports?limit=10")
        assert list_res.status_code == 200
        reports = list_res.json()
        assert isinstance(reports, list)
        assert any(r["report_id"] == report_id for r in reports)


@pytest.mark.asyncio
async def test_get_nonexistent_report():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/v1/reports/rpt_nonexistent999")
        assert res.status_code == 404
