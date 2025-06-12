import pytest


class TestQuiz:

    def test_quiz_returns_200(self, api_client):
        reponse = api_client.get('/quiz/')

        assert reponse.status_code == 200

    # Narazie nie można przetestowac, plik faiss _index zawsze istnieje NARAZIE
    @pytest.mark.skip
    def test_quiz_returns_404(self, api_client):
        reponse = api_client.get('/quiz/')

        assert reponse.status_code == 404
