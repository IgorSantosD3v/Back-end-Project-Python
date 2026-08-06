import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import Base, LivroDB, app
from fastapi.testclient import TestClient
import os


DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(bind=engine)

Base.metadata.create_all(bind=engine)

client = TestClient(app)

@pytest.fixture(autouse=True)
def mock_redis(mocker):
    mock_redis_client = mocker.patch("main.redis_client", autospec=True)
    mock_redis_client.get.return_value = None

@pytest.fixture(scope="function")
def db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_get_livros(db, mocker):
    response = client.get("/livros", auth=("admin", "admin"))
    assert response.status_code == 200

    data = response.json()

    assert len(data["livros"]) == 10
    assert data["livros"][0]["nome_livro"] == "Harry Potter"
    assert data["livros"][0]["autor_livro"] == "J.K"
    assert data["livros"][0]["ano_livro"] == 2007