class TestGetQuiz:

    def test_get_quiz_returns_200(self, api_client):
        response = api_client.get('/test/')

        assert response.status_code == 200


class TestPDF:
    def test_pdf_returns_200(self, api_client):
        response = api_client.get('/test/pdf/')

        assert response.status_code == 200


class TestEvaluate:
    def test_evaluate_returns_200(self, api_client):
        response = api_client.post('/test/evaluate/', json={'body': {}})

        print(response.json())

        assert response.status_code == 200
