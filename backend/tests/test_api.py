"""HTTP behaviour of the FastAPI app."""

import inspect

import pytest
from fastapi.testclient import TestClient

import api_endpoints
import sem_plan
from conftest import BRAND_URL, COMPETITOR_URL
from main import app
from models import PlanRequest

PAYLOAD = {
    "brand_url": BRAND_URL,
    "competitor_url": COMPETITOR_URL,
    "average_product_price": 110,
    "target_roas_percentage": 400,
}


@pytest.fixture
def client():
    return TestClient(app)


def test_health_reports_configuration_without_keys(client):
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "language_model_configured": False,
        "keyword_planner_configured": False,
    }


def test_plan_endpoint_is_sync_so_blocking_calls_run_in_threadpool():
    assert not inspect.iscoroutinefunction(api_endpoints.create_sem_plan)


def test_request_model_has_only_used_inputs(client, fake_groq):
    assert set(PlanRequest.model_fields) == {
        "brand_url",
        "competitor_url",
        "average_product_price",
        "target_roas_percentage",
    }
    bad = client.post("/api/v1/plan", json={**PAYLOAD, "brand_url": "example-brand.com"})
    assert bad.status_code == 422


def test_plan_response_marks_estimated_data(client, fake_groq):
    fake_groq(seeds="running shoes", groups={"Running": ["running shoes"]}, themes="Running shoes for trails")

    response = client.post("/api/v1/plan", json=PAYLOAD)

    assert response.status_code == 200
    body = response.json()
    assert body["data_source"] == "estimated"
    assert "not configured" in body["estimated_reason"]
    assert body["shopping_campaign_plan"]["assumed_conversion_rate"] == 0.02
    assert body["shopping_campaign_plan"]["suggested_target_cpc"] == 0.55
    assert "theme" not in body["search_campaign_plan"]["ad_groups"][0]


def test_llm_failure_returns_502_with_plain_message(client, fake_groq):
    fake_groq(error=RuntimeError("upstream exploded: internal detail 42"))

    response = client.post("/api/v1/plan", json=PAYLOAD)

    assert response.status_code == 502
    assert response.json() == {
        "detail": "The language model request failed while suggesting seed keywords. Try again in a moment."
    }
    assert "upstream exploded" not in response.text
    assert "Traceback" not in response.text


def test_missing_groq_key_returns_502(client):
    response = client.post("/api/v1/plan", json=PAYLOAD)

    assert response.status_code == 502
    assert "GROQ_API_KEY is not set" in response.json()["detail"]


def test_unreadable_ad_groups_return_502(client, fake_groq):
    fake_groq(seeds="running shoes", groups="Sure! Here are your ad groups: Running -> running shoes")

    response = client.post("/api/v1/plan", json=PAYLOAD)

    assert response.status_code == 502
    assert response.json()["detail"] == "The language model returned ad groups that could not be read as JSON."


def test_unexpected_error_returns_generic_500(client, fake_groq, monkeypatch):
    fake_groq(seeds="running shoes", groups={"Running": ["running shoes"]}, themes="Running shoes")

    def broken(ideas):
        raise ValueError("internal state dump")

    monkeypatch.setattr(sem_plan, "rank_keywords", broken)

    response = client.post("/api/v1/plan", json=PAYLOAD)

    assert response.status_code == 500
    assert "internal state dump" not in response.text
    assert response.json()["detail"].startswith("Unexpected error while generating the plan.")
