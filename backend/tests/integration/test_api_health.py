"""Integration tests for API health and basic endpoints."""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    """Create a test client."""
    with TestClient(app) as test_client:
        yield test_client


class TestHealthEndpoint:
    """Tests for health check endpoint."""

    def test_health_check_returns_200(self, client):
        """Test that health endpoint returns 200 OK."""
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_check_response_structure(self, client):
        """Test health check response has expected fields."""
        response = client.get("/health")
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"
        assert "model_loaded" in data
        assert "model_version" in data


class TestRootEndpoint:
    """Tests for root endpoint."""

    def test_root_returns_200(self, client):
        """Test that root endpoint returns 200 OK."""
        response = client.get("/")
        assert response.status_code == 200

    def test_root_response_structure(self, client):
        """Test root response has expected fields."""
        response = client.get("/")
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert "docs" in data


class TestAPIDocumentation:
    """Tests for API documentation endpoints."""

    def test_openapi_docs_available(self, client):
        """Test that OpenAPI documentation is available."""
        response = client.get("/docs")
        assert response.status_code == 200

    def test_openapi_json_available(self, client):
        """Test that OpenAPI JSON schema is available."""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        data = response.json()
        assert "openapi" in data
        assert "paths" in data
        assert "info" in data

    def test_redoc_available(self, client):
        """Test that ReDoc documentation is available."""
        response = client.get("/redoc")
        assert response.status_code == 200
