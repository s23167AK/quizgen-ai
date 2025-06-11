# import io
#
# class TestUploadFile:
#     def test_upload_returns_200(self, api_client):
#         file_content = b"Hello, this is a test file"
#         file = io.BytesIO(file_content)
#
#         response = api_client.post('/upload/', files={"file": ("test.txt", file, "text/plain")})
#
#         assert response.status_code == 200
#
#     def test_upload_empty_file_returns_400(self, api_client):
#         file_content = b""
#         file = io.BytesIO(file_content)
#
#         response = api_client.post('/upload/', files={"file": ("test.txt", file, "text/plain")})
#
#         print(response.json())
#
#         assert response.status_code == 400
#
#     def test_upload_invalid_file_returns_400(self, api_client):
#         file_content = b""
#         file = io.BytesIO(file_content)
#
#         response = api_client.post('/upload/', files={"file": ("test.md", file, "text/plain")})
#
#         print(response.json())
#
#         assert response.status_code == 400