from fastapi.testclient import TestClient
import pytest

from backend.main import app

@pytest.fixture
def api_client():
    return TestClient(app)