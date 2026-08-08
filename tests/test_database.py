import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from main import Base, LivroDB, app, sessao_db
from fastapi.testclient import TestClient


DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,  # garante que todas as conexões usem o MESMO banco em memória
)
TestingSessionLocal = sessionmaker(bind=engine)

Base.metadata.create_all(bind=engine)


def override_sessao_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[sessao_db] = override_sessao_db

client = TestClient(app)


@pytest.fixture(autouse=True)
def mock_redis(mocker):
    mock_redis_client = mocker.patch("main.redis_client", autospec=True)
    mock_redis_client.get.return_value = None


@pytest.fixture(scope="function")
def db():
    db = TestingSessionLocal()
    db.query(LivroDB).delete()  # limpa antes de cada teste
    db.commit()

    livros_seed = [
        LivroDB(nome_livro="Harry Potter", autor_livro="J.K", ano_livro=2007),
        LivroDB(nome_livro="Harry Potter 2", autor_livro="J.K", ano_livro=2008),
        LivroDB(nome_livro="Harry Potter 3", autor_livro="J.K", ano_livro=2009),
        LivroDB(nome_livro="Harry Potter 4", autor_livro="J.K", ano_livro=2010),
        LivroDB(nome_livro="Harry Potter 5", autor_livro="J.K", ano_livro=2011),
        LivroDB(nome_livro="Harry Potter 6", autor_livro="J.K", ano_livro=2012),
        LivroDB(nome_livro="Harry Potter 7", autor_livro="J.K", ano_livro=2013),
        LivroDB(nome_livro="Harry Potter 8", autor_livro="J.K", ano_livro=2014),
        LivroDB(nome_livro="Harry Potter 9", autor_livro="J.K", ano_livro=2015),
        LivroDB(nome_livro="Harry Potter 10", autor_livro="J.K", ano_livro=2016),
    ]
    db.add_all(livros_seed)
    db.commit()

    try:
        yield db
    finally:
        db.query(LivroDB).delete()
        db.commit()
        db.close()


def test_get_livros(db, mocker):
    response = client.get("/livros", auth=("admin", "admin"))
    assert response.status_code == 200

    data = response.json()

    assert len(data["livros"]) == 10
    assert data["livros"][0]["nome_livro"] == "Harry Potter"
    assert data["livros"][0]["autor_livro"] == "J.K"
    assert data["livros"][0]["ano_livro"] == 2007