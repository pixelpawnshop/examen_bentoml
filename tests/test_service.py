import pytest
from starlette.testclient import TestClient

from src.service import svc, model_runner

@pytest.fixture(autouse=True)
def mock_model_runner(monkeypatch):
    async def dummy_async_run(self, df):
        return [0.75]
    monkeypatch.setattr(type(model_runner.predict), "async_run", dummy_async_run)

@pytest.fixture(scope="module")
def bentoml_server():
    client = TestClient(svc.asgi_app)
    yield client

def get_jwt_token(client):
    response = client.post("/login", json={"username": "admin", "password": "password"})
    return response.json()["token"]

def test_login_success(bentoml_server):
    response = bentoml_server.post("/login", json={"username": "admin", "password": "password"})
    assert response.status_code == 200
    assert "token" in response.json()

def test_login_failure(bentoml_server):
    response = bentoml_server.post("/login", json={"username": "wronguser", "password": "wrongpass"})
    assert response.status_code == 401

def test_login_missing_fields(bentoml_server):
    response = bentoml_server.post("/login", json={"username": "admin"})
    assert response.status_code == 401

def test_login_empty_payload(bentoml_server):
    response = bentoml_server.post("/login", json={})
    assert response.status_code == 401

def test_prediction_success(bentoml_server):
    payload = {
        "GRE_Score": 320,
        "TOEFL_Score": 110,
        "University_Rating": 4,
        "SOP": 4.5,
        "LOR": 4.0,
        "CGPA": 9.0,
        "Research": 1
    }
    token = get_jwt_token(bentoml_server)
    headers = {"Authorization": f"Bearer {token}"}
    response = bentoml_server.post("/predict", json=payload, headers=headers)
    assert response.status_code == 200
    assert "chance_of_admit" in response.json()

def test_prediction_invalid_token(bentoml_server):
    payload = {
        "GRE_Score": 320,
        "TOEFL_Score": 110,
        "University_Rating": 4,
        "SOP": 4.5,
        "LOR": 4.0,
        "CGPA": 9.0,
        "Research": 1
    }
    headers = {"Authorization": "Bearer invalidtoken"}
    response = bentoml_server.post("/predict", json=payload, headers=headers)
    assert response.status_code == 401

def test_prediction_expired_token(bentoml_server):
    payload = {
        "GRE_Score": 320,
        "TOEFL_Score": 110,
        "University_Rating": 4,
        "SOP": 4.5,
        "LOR": 4.0,
        "CGPA": 9.0,
        "Research": 1
    }
    import jwt, datetime
    expired_payload = {
        "username": "admin",
        "exp": (datetime.datetime.utcnow() - datetime.timedelta(seconds=10)).timestamp()
    }
    expired_token = jwt.encode(expired_payload, "your_secret_key", algorithm="HS256")
    headers = {"Authorization": f"Bearer {expired_token}"}
    response = bentoml_server.post("/predict", json=payload, headers=headers)
    assert response.status_code == 401

def test_prediction_missing_fields(bentoml_server):
    payload = {
        "GRE Score": 320
    }
    token = get_jwt_token(bentoml_server)
    headers = {"Authorization": f"Bearer {token}"}
    response = bentoml_server.post("/predict", json=payload, headers=headers)
    assert response.status_code == 400

def test_prediction_invalid_input(bentoml_server):
    payload = {
        "GRE_Score": "invalid",  # Invalid type
        "TOEFL_Score": 110,
        "University_Rating": 4,
        "SOP": 4.5,
        "LOR": 4.0,
        "CGPA": 9.0,
        "Research": 1
    }
    token = get_jwt_token(bentoml_server)
    headers = {"Authorization": f"Bearer {token}"}
    response = bentoml_server.post("/predict", json=payload, headers=headers)
    assert response.status_code == 400

def test_prediction_no_token(bentoml_server):
    payload = {
        "GRE_Score": 320,
        "TOEFL_Score": 110,
        "University_Rating": 4,
        "SOP": 4.5,
        "LOR": 4.0,
        "CGPA": 9.0,
        "Research": 1
    }
    response = bentoml_server.post("/predict", json=payload)
    assert response.status_code == 401