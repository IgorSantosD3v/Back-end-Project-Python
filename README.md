# API de Livros

API REST para gerenciamento de livros com FastAPI, SQLAlchemy e SQLite, com autenticacao HTTP Basic, paginacao e CRUD completo.

## Tecnologias Utilizadas

- Python `>=3.14`
- FastAPI (`fastapi[standard]`)
- SQLAlchemy `2.x`
- SQLite + `aiosqlite`
- Poetry
- Docker e Docker Compose

## Funcionalidades

- Rota de health check (`/`)
- Listagem paginada de livros (`/livros?page=1&limit=10`)
- Cadastro de livro (`/adiciona`)
- Atualizacao de livro por ID (`/atualiza/{id_livro}`)
- Remocao de livro por ID (`/deletar/{id_livro}`)
- Protecao das rotas de livros com HTTP Basic Auth

## Variaveis de Ambiente

A aplicacao le as variaveis abaixo:

- `DATABASE_URL` (padrao: `sqlite:///./livros.db`)
- `MEU_USUARIO` (padrao: `admin`)
- `MINHA_SENHA` (padrao: `admin`)

Exemplo de `.env`:

```env
DATABASE_URL=sqlite:///./livros.db
MEU_USUARIO=admin
MINHA_SENHA=admin
```

## Estrutura do Projeto

```bash
.
├── main.py
├── pyproject.toml
├── poetry.lock
├── DockerFile
├── docker-compose.yml
└── README.md
```

## Como Rodar Localmente (Poetry)

1. Instale as dependencias:

```bash
poetry install
```

2. Suba a API:

```bash
poetry run uvicorn main:app --reload
```

API disponivel em `http://127.0.0.1:8000`.

## Como Rodar com Docker Compose

1. Crie o arquivo `.env` na raiz do projeto.
2. Execute:

```bash
docker compose up --build
```

API disponivel em `http://localhost:8000`.

Observacao: o `docker-compose.yml` possui secao `deploy` com `replicas` e `restart_policy`; essas configuracoes sao aplicadas em ambiente Swarm.

## Documentacao da API

Com a API rodando:

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`
- OpenAPI JSON: `http://127.0.0.1:8000/openapi.json`

## Endpoints

| Metodo | Rota | Descricao |
|---|---|---|
| GET | `/` | Verifica se a API esta online |
| GET | `/livros` | Lista livros com paginacao |
| POST | `/adiciona` | Adiciona um novo livro |
| PUT | `/atualiza/{id_livro}` | Atualiza um livro existente |
| DELETE | `/deletar/{id_livro}` | Remove um livro |

## Exemplos com cURL

```bash
curl -u admin:admin "http://127.0.0.1:8000/livros?page=1&limit=10"
```

```bash
curl -u admin:admin -X POST "http://127.0.0.1:8000/adiciona" \
  -H "Content-Type: application/json" \
  -d "{\"nome_livro\":\"Clean Code\",\"autor_livro\":\"Robert C. Martin\",\"ano_livro\":2008}"
```

```bash
curl -u admin:admin -X PUT "http://127.0.0.1:8000/atualiza/1" \
  -H "Content-Type: application/json" \
  -d "{\"nome_livro\":\"Clean Code (2a edicao)\",\"autor_livro\":\"Robert C. Martin\",\"ano_livro\":2009}"
```

```bash
curl -u admin:admin -X DELETE "http://127.0.0.1:8000/deletar/1"
```

## Banco de Dados

- Banco padrao: SQLite (`livros.db`, na raiz do projeto)
- A tabela `livros` e criada automaticamente na inicializacao, caso nao exista

## Autor

Igor Santos  
Email: `Igorsantosdevp@gmail.com`
