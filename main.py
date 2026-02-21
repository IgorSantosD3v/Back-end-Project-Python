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

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

# FastAPI: framework para criar APIs
# HTTPException: usado para retornar erros HTTP personalizados (404, 400, etc.)

app = FastAPI(
    title="API de Livros"
)
# Cria a aplicação FastAPI

# Dicionário que funciona como "banco de dados em memória"
# A chave será o id do livro
# O valor será outro dicionário com os dados do livro
meu_livrozinhos = {}

class Livro(BaseModel):
    nome_livro: str
    autor_livro: str
    ano_livro: int
# -------------------------------
# Rota raiz (teste)
# -------------------------------
@app.get("/")
def hello_world():
    # Endpoint simples só para testar se a API está rodando
    return {"Hello": "World!"}

# -------------------------------
# GET - Listar livros (READ)
# -------------------------------
@app.get("/livros")
def get_livros():
    # Verifica se o dicionário está vazio
    if not meu_livrozinhos:
        # Se não existir nenhum livro cadastrado
        return {"message": "Não existe nenhum livro!"}
    else:
        # Retorna todos os livros cadastrados
        return {"livros": meu_livrozinhos}

# -------------------------------
# POST - Adicionar livro (CREATE)
# -------------------------------
@app.post("/adiciona")
def post_livros(id_livro: int, livro: Livro):
    # Verifica se o id do livro já existe no "banco"
    if id_livro in meu_livrozinhos:
        # Se existir, lança erro 400 (requisição inválida)
        raise HTTPException(
            status_code=400,
            detail="Esse livro já existe, meu parceiro!"
        )
    else:
        # Se não existir, cria o livro no dicionário
        meu_livrozinhos[id_livro] = livro.model_dump()
        # Retorna mensagem de sucesso
        return {"message":"O livro foi criado com sucesso!"}

             

# -------------------------------
# PUT - Atualizar livro (UPDATE)
# -------------------------------
@app.put("/atualiza/{id_livro}")
def put_livros(id_livro: int, livro: Livro):
    # Busca o livro pelo id
    meu_livro = meu_livrozinhos.get(id_livro)

    # Se não encontrar o livro
    if not meu_livro:
        raise HTTPException(
            status_code=404,
            detail="Esse livro não foi encontrado!"
        )
    else:
        meu_livrozinhos[id_livro] = livro.model_dump()
        # Atualiza os campos do livro
        # (aqui você está modificando o dicionário existente)
        return {
            "message": "As informações do seu livro foram atualizadas com sucesso!"
        }

# -------------------------------
# DELETE - Remover livro (DELETE)
# -------------------------------
@app.delete("/deletar/{id_livro}")
def delete_livro(id_livro: int):
    # Verifica se o livro existe
    if id_livro not in meu_livrozinhos:
        raise HTTPException(
            status_code=404,
            detail="Esse livro não foi encontrado!"
        )
    else:
        # Remove o livro do dicionário
        del meu_livrozinhos[id_livro]

        return {"message": "Seu livro foi deletado com sucesso!"}
