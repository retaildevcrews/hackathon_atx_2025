import json
import httpx
import pytest
from upload_client import UploadClient, AuthError, ValidationError, ServerError, UploadError

class DummyTransport(httpx.BaseTransport):
    def __init__(self, handler):
        self.handler = handler
    def handle_request(self, request):  # type: ignore[override]
        return self.handler(request)

class ResponseFactory:
    @staticmethod
    def make(status: int, json_body=None, text=None):
        content = b""
        headers = {"Content-Type": "application/json"}
        if json_body is not None:
            content = json.dumps(json_body).encode()
        elif text is not None:
            content = text.encode()
            headers = {"Content-Type": "text/plain"}
        stream = httpx.ByteStream(content)
        return httpx.Response(status_code=status, headers=headers, stream=stream)


def build_client(status: int, json_body=None, text=None):
    def handler(request: httpx.Request):
        return ResponseFactory.make(status, json_body=json_body, text=text)
    transport = DummyTransport(handler)
    c = UploadClient(endpoint="http://test")
    c._client = httpx.Client(transport=transport)
    return c


def test_success():
    client = build_client(200, json_body={"blobPath": "a/b/c.txt", "sha256": "abc", "size": 5})
    import io
    res = client.upload("candidate", "123", io.BytesIO(b"hello"), "c.txt")
    assert res.blob_path == "a/b/c.txt"
    assert res.size == 5


def test_unauthorized():
    client = build_client(401, text="unauthorized")
    import io
    with pytest.raises(AuthError):
        client.upload("candidate", "123", io.BytesIO(b"hello"), "c.txt")


def test_validation():
    client = build_client(400, text="bad ctx")
    import io
    with pytest.raises(ValidationError):
        client.upload("candidate", "123", io.BytesIO(b"hello"), "c.txt")


def test_server_error():
    client = build_client(500, text="boom")
    import io
    with pytest.raises(ServerError):
        client.upload("candidate", "123", io.BytesIO(b"hello"), "c.txt")


def test_unexpected_status():
    client = build_client(418, text="teapot")
    import io
    with pytest.raises(UploadError):
        client.upload("candidate", "123", io.BytesIO(b"hello"), "c.txt")


def test_missing_endpoint_env():
    with pytest.raises(ValueError):
        UploadClient(endpoint="")
