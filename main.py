# ================================
# API de Livros com FastAPI
# ================================

# Aqui eu estou criando uma API REST simples para gerenciar livros.
# Ela segue o padrão CRUD:
# Create  -> POST
# Read    -> GET
# Update  -> PUT
# Delete  -> DELETE
# Documentação Swagger/ Serve para compartilhar nossos endpoints atraves da nossa API, como por exemplo, Outra equipe tecnica.

from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
import secrets

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

DATABASE_URL = "sqlite:///./livros.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# FastAPI: framework para criar APIs
# HTTPException: usado para retornar erros HTTP personalizados (404, 400, etc.)

app = FastAPI(
    title="API de Livros"
)

MEU_USUARIO = "admin"
MINHA_SENHA = "admin"

security = HTTPBasic()

meu_livrozinhos = {}
# Cria a aplicação FastAPI

# Dicionário que funciona como "banco de dados em memória"
# A chave será o id do livro
# O valor será outro dicionário com os dados do livro
meu_livrozinhos = {}

class LivroDB(Base):
    __tablename__ = "livros"
    id = Column(Integer, primary_key=True, index=True)
    nome_livro = Column(String, index=True)
    autor_livro = Column(String, index=True)
    ano_livro = Column(Integer, index=True)



class Livro(BaseModel):
    nome_livro: str
    autor_livro: str
    ano_livro: int
    
Base.metadata.create_all(bind=engine)

def sessao_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
# -------------------------------
# Rota raiz (teste)
# -------------------------------
def autenticar_meu_usuario(credentials: HTTPBasicCredentials = Depends(security)):
    is_username_correct = secrets.compare_digest(credentials.username, MEU_USUARIO)
    is_password_correct = secrets.compare_digest(credentials.password, MINHA_SENHA)
    
    if not (is_username_correct and is_password_correct):
        raise HTTPException(
            status_code=401,
            detail="Usuário ou senha incorretos",
            headers={"WWW-Authenticate": "Basic"}
        )


@app.get("/")
def hello_world():
    # Endpoint simples só para testar se a API está rodando
    return {"Hello": "World!"}

# -------------------------------
# GET - Listar livros (READ)
# -------------------------------
@app.get("/livros")
def get_livros(page: int = 1, limit: int = 10, db: Session = Depends(sessao_db), credentials: HTTPBasicCredentials = Depends(autenticar_meu_usuario)):
  if page < 1 or limit < 1:
      raise HTTPException(status_code=400, detail="Page ou limit estão com valores inválidos!")

  livros = db.query(LivroDB).offset((page - 1) * limit).limit(limit).all()

  if not livros:
      return {"message": "Não existe nenhum livro!"}
  
  total_livros = db.query(LivroDB).count()
  
  return{
      "page": page,
      "limit": limit,
      "total": total_livros,
      "livros": [{"id": livro.id, "nome_livro": livro.nome_livro, "autor_livro": livro.autor_livro, "ano_livro": livro.ano_livro} for livro in livros]
  }
# -------------------------------
# POST - Adicionar livro (CREATE)
# -------------------------------

@app.post("/adiciona")
def post_livros (livro: Livro, db: Session = Depends(sessao_db), credentials: HTTPBasicCredentials = Depends(autenticar_meu_usuario)):
    db_livro = db.query(LivroDB).filter(LivroDB.nome_livro == livro.nome_livro, LivroDB.autor_livro == livro.autor_livro).first()
    if db_livro:
        raise HTTPException(status_code=400, detail="Esse livro já existe!")
    
    novo_livro = LivroDB(nome_livro=livro.nome_livro, autor_livro=livro.autor_livro, ano_livro=livro.ano_livro)
    db.add(novo_livro)
    db.commit()
    db.refresh(novo_livro)
    return {
        "message": "Seu livro foi adicionado com sucesso!",
        "livro": {
            "id": novo_livro.id,
            "nome_livro": novo_livro.nome_livro,
            "autor_livro": novo_livro.autor_livro,
            "ano_livro": novo_livro.ano_livro
        }
    }
             

# -------------------------------
# PUT - Atualizar livro (UPDATE)
# -------------------------------
@app.put("/atualiza/{id_livro}")
def put_livros(id_livro: int, livro: Livro, db: Session = Depends(sessao_db), credentials: HTTPBasicCredentials = Depends(autenticar_meu_usuario)):
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
            "ano_livro": db_livro.ano_livro
        }
    }

# -------------------------------
# DELETE - Remover livro (DELETE)
# -------------------------------
@app.delete("/deletar/{id_livro}")
def delete_livro(id_livro: int, db: Session = Depends(sessao_db), credentials: HTTPBasicCredentials = Depends(autenticar_meu_usuario)):
    # Verifica se o livro existe
    db_livro = db.query(LivroDB).filter(LivroDB.id == id_livro).first()
    if not db_livro:
        raise HTTPException(
            status_code=404,
            detail="Esse livro não foi encontrado!"
        )
    else:
        db.delete(db_livro)
        db.commit()
        return {"message": "Seu livro foi deletado com sucesso!"}
