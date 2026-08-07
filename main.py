"""API de Livros — FastAPI + SQLAlchemy + Celery + Kafka + Elasticsearch."""

import asyncio
import logging
import logging.config
import os
import secrets
from datetime import datetime

import redis
import yaml
from celery.result import AsyncResult
from elasticsearch import Elasticsearch
from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from sqlalchemy import Integer, String, create_engine
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    Session,
    mapped_column,
    sessionmaker,
)

from celery_app import celery_app
from kafka_producer import enviar_evento
from tasks import fatorial, somar

# --------------------------------------------------------------------------
# Configuração
# --------------------------------------------------------------------------

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./livros.db")
ELASTICSEARCH_URL = os.getenv("ELASTICSEARCH_URL", "http://localhost:9200")
ELASTICSEARCH_INDEX = os.getenv("ELASTICSEARCH_INDEX", "livros-logs")
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = os.getenv("REDIS_PORT", 6379)
MEU_USUARIO = os.getenv("MEU_USUARIO", "admin")
MINHA_SENHA = os.getenv("MINHA_SENHA", "admin")

with open("logging_config.yaml", "r") as f:
    logging_config = yaml.safe_load(f)

log_file_path = os.getenv("LOG_FILE_PATH")
if log_file_path:
    # Handler de arquivo só é ativado quando LOG_FILE_PATH está definido
    # (ex: dentro do Docker). Localmente, com `fastapi dev`, ele fica
    # desativado — caso contrário, o watcher do reload detecta a escrita
    # do próprio log como "mudança de arquivo" e entra em loop de restart.
    os.makedirs(os.path.dirname(log_file_path) or ".", exist_ok=True)
    logging_config["handlers"]["file"]["filename"] = log_file_path
else:
    logging_config["handlers"].pop("file", None)
    logging_config["root"]["handlers"] = [
        h for h in logging_config["root"]["handlers"] if h != "file"
    ]

logging.config.dictConfig(logging_config)

logger = logging.getLogger(__name__)

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
es_client = Elasticsearch(hosts=[ELASTICSEARCH_URL])
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True)
security = HTTPBasic()

app = FastAPI(
    title="API de Livros",
    description="API para gerenciar catálogo de livros.",
    version="1.0.0",
    contact={"name": "Igor Santos", "email": "igorsantosdevp@gmail.com"},
)


class Base(DeclarativeBase):
    pass


# --------------------------------------------------------------------------
# Modelos
# --------------------------------------------------------------------------

class LivroDB(Base):
    __tablename__ = "livros"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nome_livro: Mapped[str] = mapped_column(String, index=True)
    autor_livro: Mapped[str] = mapped_column(String, index=True)
    ano_livro: Mapped[int] = mapped_column(Integer, index=True)


class Livro(BaseModel):
    nome_livro: str
    autor_livro: str
    ano_livro: int


Base.metadata.create_all(bind=engine)


# --------------------------------------------------------------------------
# Dependências
# --------------------------------------------------------------------------

def sessao_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def autenticar_meu_usuario(credentials: HTTPBasicCredentials = Depends(security)) -> HTTPBasicCredentials:
    usuario_ok = secrets.compare_digest(credentials.username, MEU_USUARIO)
    senha_ok = secrets.compare_digest(credentials.password, MINHA_SENHA)

    if not (usuario_ok and senha_ok):
        raise HTTPException(
            status_code=401,
            detail="Usuário ou senha incorretos",
            headers={"WWW-Authenticate": "Basic"},
        )

    return credentials


def registrar_log_elasticsearch(**dados):
    """Envia um log estruturado para o Elasticsearch sem derrubar a request em caso de falha."""
    try:
        es_client.index(index=ELASTICSEARCH_INDEX, body={"timestamp": datetime.utcnow().isoformat(), **dados})
    except Exception as e:
        logger.error(f"Erro ao enviar log para Elasticsearch: {e}")


# --------------------------------------------------------------------------
# Rotas básicas
# --------------------------------------------------------------------------

@app.get("/")
def hello_world():
    logger.info("Rota raiz acessada com sucesso.")
    return {"Hello": "World!"}


# --------------------------------------------------------------------------
# Tarefas assíncronas (Celery)
# --------------------------------------------------------------------------

def _enfileirar_tarefa(tarefa, mensagem: str):
    redis_client.lpush("tarefas_ids", tarefa.id)
    redis_client.ltrim("tarefas_ids", 0, 49)  # mantém só os últimos 50 IDs
    return {"task_id": tarefa.id, "message": mensagem}


@app.post("/calcular/soma")
def calcular_soma(a: int, b: int):
    return _enfileirar_tarefa(
        somar.delay(a, b),
        "A soma está sendo processada em segundo plano. Use o task_id para verificar o status.",
    )


@app.post("/calcular/fatorial")
def calcular_fatorial(n: int):
    return _enfileirar_tarefa(
        fatorial.delay(n),
        "O cálculo do fatorial está sendo processado em segundo plano. Use o task_id para verificar o status.",
    )


@app.get("/tarefas/recentes")
def listar_tarefas_recentes():
    tarefas = []
    for task_id in redis_client.lrange("tarefas_ids", 0, -1):
        resultado = AsyncResult(task_id, app=celery_app)
        tarefas.append({
            "task_id": task_id,
            "status": resultado.status,
            "result": resultado.result if resultado.status == "SUCCESS" else None,
        })
    return {"tarefas": tarefas}


# --------------------------------------------------------------------------
# Chamadas externas concorrentes (demo de asyncio)
# --------------------------------------------------------------------------

async def _chamada_externa(segundos: int, resultado: str) -> str:
    await asyncio.sleep(segundos)
    return resultado


@app.get("/chamadas-externas")
async def chamadas_externas():
    tarefas = [
        asyncio.create_task(_chamada_externa(2, "Resultado da chamada externa 1")),
        asyncio.create_task(_chamada_externa(3, "Resultado da chamada externa 2")),
        asyncio.create_task(_chamada_externa(1, "Resultado da chamada externa 3")),
    ]
    resultados = await asyncio.gather(*tarefas)
    return {
        "mensagem": "Todas as chamadas externas foram concluídas!",
        "resultados": resultados,
    }


# --------------------------------------------------------------------------
# CRUD de livros
# --------------------------------------------------------------------------

@app.get("/livros")
async def get_livros(
    page: int = 1,
    limit: int = 10,
    db: Session = Depends(sessao_db),
    credentials: HTTPBasicCredentials = Depends(autenticar_meu_usuario),
):
    if page < 1 or limit < 1:
        raise HTTPException(status_code=400, detail="Page ou limit estão com valores inválidos!")

    livros = db.query(LivroDB).offset((page - 1) * limit).limit(limit).all()

    if not livros:
        return {"message": "Não existe nenhum livro!"}

    response = {
        "page": page,
        "limit": limit,
        "total_livros": db.query(LivroDB).count(),
        "livros": [
            {
                "id": livro.id,
                "nome_livro": livro.nome_livro,
                "autor_livro": livro.autor_livro,
                "ano_livro": livro.ano_livro,
            }
            for livro in livros
        ],
    }

    registrar_log_elasticsearch(
        endpoint="/livros",
        usuario=credentials.username,
        page=page,
        limit=limit,
        status="success",
        total_livros=len(livros),
    )

    return response


@app.post("/adiciona")
async def post_livros(
    livro: Livro,
    db: Session = Depends(sessao_db),
    credentials: HTTPBasicCredentials = Depends(autenticar_meu_usuario),
):
    ja_existe = (
        db.query(LivroDB)
        .filter(LivroDB.nome_livro == livro.nome_livro, LivroDB.autor_livro == livro.autor_livro)
        .first()
    )
    if ja_existe:
        raise HTTPException(status_code=400, detail="Esse livro já existe!")

    novo_livro = LivroDB(**livro.dict())
    db.add(novo_livro)
    db.commit()
    db.refresh(novo_livro)

    enviar_evento("livros_eventos", {"acao": "criar", "livro": livro.dict()})

    return {
        "message": "Seu livro foi adicionado com sucesso!",
        "livro": {
            "id": novo_livro.id,
            "nome_livro": novo_livro.nome_livro,
            "autor_livro": novo_livro.autor_livro,
            "ano_livro": novo_livro.ano_livro,
        },
    }


@app.put("/atualiza/{id_livro}")
async def put_livros(
    id_livro: int,
    livro: Livro,
    db: Session = Depends(sessao_db),
    credentials: HTTPBasicCredentials = Depends(autenticar_meu_usuario),
):
    db_livro = db.query(LivroDB).filter(LivroDB.id == id_livro).first()
    if not db_livro:
        raise HTTPException(status_code=404, detail="Esse livro não foi encontrado!")

    db_livro.nome_livro = livro.nome_livro
    db_livro.autor_livro = livro.autor_livro
    db_livro.ano_livro = livro.ano_livro
    db.commit()
    db.refresh(db_livro)

    return {
        "message": "Seu livro foi atualizado com sucesso!",
        "livro": {
            "id": db_livro.id,
            "nome_livro": db_livro.nome_livro,
            "autor_livro": db_livro.autor_livro,
            "ano_livro": db_livro.ano_livro,
        },
    }


@app.delete("/deletar/{id_livro}")
async def delete_livro(
    id_livro: int,
    db: Session = Depends(sessao_db),
    credentials: HTTPBasicCredentials = Depends(autenticar_meu_usuario),
):
    db_livro = db.query(LivroDB).filter(LivroDB.id == id_livro).first()
    if not db_livro:
        raise HTTPException(status_code=404, detail="Esse livro não foi encontrado!")

    db.delete(db_livro)
    db.commit()

    return {"message": "Seu livro foi deletado com sucesso!"}