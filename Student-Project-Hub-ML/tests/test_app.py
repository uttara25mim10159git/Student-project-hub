import tempfile
import os
import pytest
from app import app, init_db

@pytest.fixture
def client(monkeypatch):
    fd, path = tempfile.mkstemp()
    os.close(fd)
    monkeypatch.setattr("app.DB_PATH", path)
    app.config["TESTING"] = True
    with app.test_client() as client:
        init_db()
        yield client
    os.remove(path)

def test_home_page(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Student Project Hub" in response.data

def test_register_and_login(client):
    response = client.post("/register", data={
        "name":"Test Student", "email":"test@example.com",
        "password":"password123", "branch":"AI/ML", "year":"2"
    }, follow_redirects=True)
    assert b"Account created" in response.data

    response = client.post("/login", data={
        "email":"test@example.com", "password":"password123"
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Dashboard" in response.data

def test_projects_page(client):
    response = client.get("/projects")
    assert response.status_code == 200
    assert b"Student Projects" in response.data
