import pytest
from fastapi.testclient import TestClient
from src.service import app  # Assuming your FastAPI app is defined in service.py

client = TestClient(app)

def test_login_success():
    response = client.post("/login", json={"username": "testuser", "password": "testpass"})
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_login_failure():
    response = client.post("/login", json={"username": "wronguser", "password": "wrongpass"})
    assert response.status_code == 401

def test_prediction_success():
    # Assuming the model requires these fields for prediction
    payload = {
        "GRE Score": 320,
        "TOEFL Score": 110,
        "University Rating": 4,
        "SOP": 4.5,
        "LOR": 4.0,
        "CGPA": 9.0,
        "Research": 1
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    assert "prediction" in response.json()

def test_prediction_failure():
    payload = {
        "GRE Score": "invalid",  # Invalid input
        "TOEFL Score": 110,
        "University Rating": 4,
        "SOP": 4.5,
        "LOR": 4.0,
        "CGPA": 9.0,
        "Research": 1
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 422  # Unprocessable Entity for invalid input

def test_authentication_required_for_prediction():
    response = client.post("/predict", json={})  # No token provided
    assert response.status_code == 401  # Unauthorized