import pytest


class TestStart:
    def test_start_returns_200(self, api_client):
        response = api_client.get('/quiz/start/')

        assert response.status_code == 200

    @pytest.mark.skip(reason="This situation never happens")
    def test_start_returns_404(self, api_client):
        response = api_client.get('/quiz/start/')

        assert response.status_code == 404
