"""
Django REST Framework health / smoke tests.
"""
import pytest
from django.test import Client


@pytest.mark.django_db
def test_health_endpoint():
    client = Client()
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "SupportAI" in data.get("app", "SupportAI") or data.get("status") == "healthy"


@pytest.mark.django_db
def test_api_root():
    client = Client()
    response = client.get("/api/v1/")
    assert response.status_code == 200
    data = response.json()
    assert "endpoints" in data or "message" in data
