from fastapi.testclient import TestClient

from app.main import app


def test_frontend_is_served_from_same_origin() -> None:
    with TestClient(app) as client:
        response = client.get("/app/")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "mAInstream" in response.text


def test_frontend_assets_are_served() -> None:
    with TestClient(app) as client:
        script_response = client.get("/app/app.js")
        style_response = client.get("/app/styles.css")

    assert script_response.status_code == 200
    assert "javascript" in script_response.headers["content-type"]
    assert style_response.status_code == 200
    assert "text/css" in style_response.headers["content-type"]
