```markdown
# API de Livros

API REST para gerenciamento de livros com **FastAPI**, **SQLAlchemy** e **SQLite**, com autenticação básica e operações completas de CRUD.

## Visão Geral

Este projeto foi criado para praticar e demonstrar:

- Construção de API com FastAPI
- Integração com banco relacional usando SQLAlchemy ORM
- Validação de dados com Pydantic
- Autenticação via HTTP Basic
- Paginação em listagens

## Stack

- Python `>=3.14`
- FastAPI
- SQLAlchemy
- SQLite
- Poetry (gerenciamento de dependências)

## Funcionalidades

- Criar livro
- Listar livros com paginação (`page` e `limit`)
- Atualizar livro por ID
- Deletar livro por ID
- Proteção das rotas com autenticação

## Estrutura do Projeto

```bash
.
├── main.py
├── pyproject.toml
└── poetry.lock
```

## Como Rodar Localmente

### 1) Instalar dependências

```bash
poetry install
```

### 2) Subir servidor em desenvolvimento

```bash
poetry run uvicorn main:app --reload
```

Servidor disponível em: `http://127.0.0.1:8000`

## Documentação da API

Com o servidor rodando:

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`
- OpenAPI JSON: `http://127.0.0.1:8000/openapi.json`

## Autenticação

As rotas de livros usam **HTTP Basic Auth**.

Credenciais atuais (ambiente de estudo):

- Usuário: `admin`
- Senha: `admin`

## Endpoints

| Método | Rota | Descrição |
|---|---|---|
| GET | `/` | Health-check simples (`Hello World`) |
| GET | `/livros` | Lista livros com paginação |
| POST | `/adiciona` | Adiciona novo livro |
| PUT | `/atualiza/{id_livro}` | Atualiza livro existente |
| DELETE | `/deletar/{id_livro}` | Remove livro |

## Exemplos de Requisição (cURL)

### Listar livros (paginado)

```bash
curl -u admin:admin "http://127.0.0.1:8000/livros?page=1&limit=10"
```

### Adicionar livro

```bash
curl -u admin:admin -X POST "http://127.0.0.1:8000/adiciona" \
  -H "Content-Type: application/json" \
  -d "{\"nome_livro\":\"Clean Code\",\"autor_livro\":\"Robert C. Martin\",\"ano_livro\":2008}"
```

### Atualizar livro

```bash
curl -u admin:admin -X PUT "http://127.0.0.1:8000/atualiza/1" \
  -H "Content-Type: application/json" \
  -d "{\"nome_livro\":\"Clean Code (2ª edição)\",\"autor_livro\":\"Robert C. Martin\",\"ano_livro\":2009}"
```

### Deletar livro

```bash
curl -u admin:admin -X DELETE "http://127.0.0.1:8000/deletar/1"
```

## Banco de Dados

O projeto usa SQLite e cria automaticamente o arquivo:

- `livros.db` (na raiz do projeto)

A tabela `livros` também é criada automaticamente na inicialização, caso não exista.

## Melhorias Futuras

- Trocar credenciais fixas por variáveis de ambiente
- Implementar autenticação com JWT
- Adicionar testes automatizados (pytest)
- Adicionar Dockerfile e docker-compose
- Criar CI com GitHub Actions

## Autor

Igor Santos
Email:
```
`Igorsantosdevp@gmail.com`
```
