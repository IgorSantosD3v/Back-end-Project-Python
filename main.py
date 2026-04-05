# ================================
# API de Livros com FastAPI
# ================================
#
# Objetivo deste arquivo:
# criar uma API REST para gerenciar livros usando:
# 1) FastAPI para as rotas HTTP
# 2) SQLAlchemy para conversar com o banco SQLite
# 3) Pydantic para validar os dados recebidos nas requisições
#
# A API segue o padrão CRUD:
# - Create (criar)   -> POST
# - Read (ler -> buscar) -> GET
# - Update (atualizar) -> PUT
# - Delete (deletar) -> DELETE

# Importa as classes principais do FastAPI:
# - FastAPI: cria a aplicação
# - Depends: sistema de injeção de dependências
# - HTTPException: gera erros HTTP padronizados (400, 401, 404 etc.)
from fastapi import FastAPI, Depends, HTTPException

# Importa utilitários de autenticação Basic Auth:
# - HTTPBasic: define o "esquema" de segurança
# - HTTPBasicCredentials: carrega usuário e senha enviados no request
from fastapi.security import HTTPBasic, HTTPBasicCredentials

# BaseModel é usado para definir "modelos de entrada" e validar dados automaticamente.
from pydantic import BaseModel

# secrets.compare_digest faz comparação segura de strings (evita timing attacks).
import secrets

# SQLAlchemy:
# - create_engine: cria a conexão com o banco
# - Column, Integer, String: definem colunas e tipos da tabela
from sqlalchemy import create_engine, Column, Integer, String

# declarative_base cria a classe base para os modelos ORM.
from sqlalchemy.ext.declarative import declarative_base

# Session e sessionmaker gerenciam sessões/conexões com o banco.
from sqlalchemy.orm import Session, sessionmaker

# String de conexão com SQLite.
# "sqlite:///./livros.db" cria/usa um arquivo "livros.db" na pasta do projeto.
DATABASE_URL = "sqlite:///./livros.db"

# Cria o "engine" (ponte entre Python e banco).
# check_same_thread=False é comum no SQLite para uso com FastAPI.
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Fabrica de sessões do banco:
# - autocommit=False: precisamos dar commit manualmente
# - autoflush=False: evita flush automático em momentos inesperados
# - bind=engine: vincula essa sessão ao engine criado acima
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Classe base para nossos modelos ORM.
Base = declarative_base()

# Cria a aplicação FastAPI e define o título da documentação automática.
app = FastAPI(title="API de Livros")

# Credenciais fixas para exemplo didático.
# Em produção, isso deveria vir de variáveis de ambiente ou banco.
MEU_USUARIO = "admin"
MINHA_SENHA = "admin"

# Ativa o esquema HTTP Basic para autenticação.
security = HTTPBasic()


# Modelo ORM (tabela no banco)
class LivroDB(Base):
    # Nome da tabela no banco de dados.
    __tablename__ = "livros"

    # id: chave primária única de cada livro.
    id = Column(Integer, primary_key=True, index=True)

    # Demais campos do livro.
    # index=True acelera algumas consultas de busca.
    nome_livro = Column(String, index=True)
    autor_livro = Column(String, index=True)
    ano_livro = Column(Integer, index=True)


# Modelo de validação da API (corpo da requisição).
# Tudo que chegar em POST/PUT neste formato será validado.
class Livro(BaseModel):
    nome_livro: str
    autor_livro: str
    ano_livro: int


# Cria as tabelas no banco se ainda não existirem.
Base.metadata.create_all(bind=engine)


# Dependência de sessão do banco:
# abre uma sessão por requisição e garante fechamento ao final.
def sessao_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Dependência de autenticação:
# será "injetada" nas rotas que exigem usuário e senha.
def autenticar_meu_usuario(
    credentials: HTTPBasicCredentials = Depends(security),
):
    # Compara usuário/senha enviados com os valores esperados.
    is_username_correct = secrets.compare_digest(
        credentials.username,
        MEU_USUARIO,
    )
    is_password_correct = secrets.compare_digest(
        credentials.password,
        MINHA_SENHA,
    )

    # Se algum dado estiver incorreto, retorna 401.
    if not (is_username_correct and is_password_correct):
        raise HTTPException(
            status_code=401,
            detail="Usuário ou senha incorretos",
            headers={"WWW-Authenticate": "Basic"},
        )


# -------------------------------
# Rota raiz (teste de funcionamento)
# -------------------------------
@app.get("/")
def hello_world():
    # Endpoint simples para verificar rapidamente se a API está ativa.
    return {"Hello": "World!"}


# -------------------------------
# GET - Listar livros (READ)
# -------------------------------
@app.get("/livros")
def get_livros(
    # Paginação:
    # - page: número da página (começando em 1)
    # - limit: quantidade de itens por página
    page: int = 1,
    limit: int = 10,
    # Injeção da sessão do banco
    db: Session = Depends(sessao_db),
    # Injeção da autenticação (obrigatória nesta rota)
    credentials: HTTPBasicCredentials = Depends(autenticar_meu_usuario),
):
    # Validação básica dos parâmetros de paginação.
    if page < 1 or limit < 1:
        raise HTTPException(
            status_code=400,
            detail="Page ou limit estão com valores inválidos!",
        )

    # Consulta paginada:
    # offset "pula" registros das páginas anteriores.
    livros = db.query(LivroDB).offset((page - 1) * limit).limit(limit).all()

    # Se não houver livros, devolve mensagem amigável.
    if not livros:
        return {"message": "Não existe nenhum livro!"}

    # Conta total de livros para o frontend saber quantos itens existem no banco.
    total_livros = db.query(LivroDB).count()

    # Retorno em formato JSON.
    return {
        "page": page,
        "limit": limit,
        "total": total_livros,
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


# -------------------------------
# POST - Adicionar livro (CREATE)
# -------------------------------
@app.post("/adiciona")
def post_livros(
    # "livro" chega no corpo da requisição e é validado por Pydantic.
    livro: Livro,
    db: Session = Depends(sessao_db),
    credentials: HTTPBasicCredentials = Depends(autenticar_meu_usuario),
):
    # Verifica se já existe livro com mesmo nome + autor para evitar duplicidade.
    db_livro = (
        db.query(LivroDB)
        .filter(
            LivroDB.nome_livro == livro.nome_livro,
            LivroDB.autor_livro == livro.autor_livro,
        )
        .first()
    )
    if db_livro:
        raise HTTPException(status_code=400, detail="Esse livro já existe!")

    # Cria um objeto ORM com os dados recebidos.
    novo_livro = LivroDB(
        nome_livro=livro.nome_livro,
        autor_livro=livro.autor_livro,
        ano_livro=livro.ano_livro,
    )

    # Persistência no banco:
    # add -> commit -> refresh (refresh traz dados atualizados, como o ID gerado).
    db.add(novo_livro)
    db.commit()
    db.refresh(novo_livro)

    # Resposta de sucesso com os dados salvos.
    return {
        "message": "Seu livro foi adicionado com sucesso!",
        "livro": {
            "id": novo_livro.id,
            "nome_livro": novo_livro.nome_livro,
            "autor_livro": novo_livro.autor_livro,
            "ano_livro": novo_livro.ano_livro,
        },
    }


# -------------------------------
# PUT - Atualizar livro (UPDATE)
# -------------------------------
@app.put("/atualiza/{id_livro}")
def put_livros(
    # id_livro vem da URL, por isso está entre chaves na rota.
    id_livro: int,
    # "livro" vem no corpo, com os novos dados.
    livro: Livro,
    db: Session = Depends(sessao_db),
    credentials: HTTPBasicCredentials = Depends(autenticar_meu_usuario),
):
    # Busca no banco pelo id informado.
    db_livro = db.query(LivroDB).filter(LivroDB.id == id_livro).first()

    # Se não existir, retorna 404.
    if not db_livro:
        raise HTTPException(status_code=404, detail="Esse livro não foi encontrado!")

    # Atualiza os campos do registro.
    db_livro.nome_livro = livro.nome_livro
    db_livro.autor_livro = livro.autor_livro
    db_livro.ano_livro = livro.ano_livro

    # Salva mudanças.
    db.commit()
    db.refresh(db_livro)

    # Retorna o livro atualizado.
    return {
        "message": "Seu livro foi atualizado com sucesso!",
        "livro": {
            "id": db_livro.id,
            "nome_livro": db_livro.nome_livro,
            "autor_livro": db_livro.autor_livro,
            "ano_livro": db_livro.ano_livro,
        },
    }


# -------------------------------
# DELETE - Remover livro (DELETE)
# -------------------------------
@app.delete("/deletar/{id_livro}")
def delete_livro(
    id_livro: int,
    db: Session = Depends(sessao_db),
    credentials: HTTPBasicCredentials = Depends(autenticar_meu_usuario),
):
    # Primeiro, procura o livro.
    db_livro = db.query(LivroDB).filter(LivroDB.id == id_livro).first()

    # Se não achar, devolve erro 404.
    if not db_livro:
        raise HTTPException(
            status_code=404,
            detail="Esse livro não foi encontrado!",
        )

    # Se achar, remove e confirma a transação.
    db.delete(db_livro)
    db.commit()

    # Mensagem final de sucesso.
    return {"message": "Seu livro foi deletado com sucesso!"}
    
