from fastapi.testclient import TestClient
import pytest

from main import app

@pytest.fixture
def api_client():
    return TestClient(app)