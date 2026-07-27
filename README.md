# API de Livros

API REST para gerenciamento de livros com FastAPI, SQLAlchemy e SQLite.

O projeto implementa:
- CRUD completo de livros
- autenticação HTTP Basic nas rotas de livros
- paginação na listagem
- exemplo de concorrência assíncrona com `asyncio`
- execução local com `venv` e `requirements.txt`
- orquestração de container via `podman-compose`/Docker Compose
- worker Celery usando Redis

## Stack

- Python `>=3.14`
- FastAPI
- SQLAlchemy `2.x`
- Pydantic
- Celery
- Redis
- SQLite
- Podman / Docker

## O que mudou

O projeto agora usa `requirements.txt` para instalação local e o contêiner é construído com:
- `Dockerfile` + `requirements.txt`
- `docker-compose.yml` / `podman-compose.yml` para orquestração

A execução local não depende mais de Poetry obrigatoriamente.

## Arquivos principais

- `main.py`: aplicação FastAPI, modelos, rotas, autenticação e banco
- `tasks.py`: tarefas Celery (`somar`, `fatorial`)
- `celery_app.py`: configuração do Celery com broker Redis
- `Dockerfile`: define a imagem do container da API
- `docker-compose.yml`: orquestra `app`, `redis` e `celery`
- `requirements.txt`: dependências Python usadas no projeto
- `.env`: variáveis de ambiente para a aplicação

## Variáveis de ambiente

Variáveis lidas pela aplicação:
- `DATABASE_URL` — padrão: `sqlite:///./livros.db`
- `MEU_USUARIO` — padrão: `admin`
- `MINHA_SENHA` — padrão: `admin`

Exemplo de `.env`:

```env
MEU_USUARIO=admin
MINHA_SENHA=admin
DATABASE_URL=sqlite:///./livros.db
PYTHONUNBUFFERED=1
```

## Endpoints

### Sem autenticação

| Método | Rota | Descrição |
|---|---|---|
| GET | `/` | Health check da API |
| GET | `/chamadas-externas` | Simula 3 chamadas assíncronas concorrentes |

### Com HTTP Basic Auth

| Método | Rota | Descrição |
|---|---|---|
| GET | `/livros?page=1&limit=10` | Lista livros com paginação |
| POST | `/adiciona` | Cadastra um livro |
| PUT | `/atualiza/{id_livro}` | Atualiza um livro pelo ID |
| DELETE | `/deletar/{id_livro}` | Remove um livro pelo ID |

## Execução local

### Usando `venv`

No PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

No Linux / WSL:

```bash
python -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

A API ficará disponível em:
- `http://127.0.0.1:8000`

## Execução com container

### Recomendado: WSL + Podman Compose

Se você usa Windows com WSL, a forma mais confiável é rodar o `podman-compose` dentro do Ubuntu:

```bash
cd /mnt/c/Users/Usuario/Desktop/Back-end-Project-Python
podman-compose up --build
```

Se quiser parar os serviços:

```bash
podman-compose down
```

### Alternativa: Docker Compose

Se você tiver Docker instalado no Windows:

```bash
docker compose up --build
```

> Observação: `podman-compose` precisa do binário `podman` acessível no sistema. No Windows, usar diretamente o terminal WSL é a forma recomendada.

## Uso do projeto

### Verificar se está rodando

```bash
curl http://127.0.0.1:8000/
```

### Listar livros

```bash
curl -u admin:admin "http://127.0.0.1:8000/livros?page=1&limit=10"
```

### Adicionar livro

```bash
curl -u admin:admin -X POST "http://127.0.0.1:8000/adiciona" \
  -H "Content-Type: application/json" \
  -d '{"nome_livro":"Clean Code","autor_livro":"Robert C. Martin","ano_livro":2008}'
```

### Atualizar livro

```bash
curl -u admin:admin -X PUT "http://127.0.0.1:8000/atualiza/1" \
  -H "Content-Type: application/json" \
  -d '{"nome_livro":"Clean Code (2a edicao)","autor_livro":"Robert C. Martin","ano_livro":2009}'
```

### Deletar livro

```bash
curl -u admin:admin -X DELETE "http://127.0.0.1:8000/deletar/1"
```

## Estrutura do projeto

```text
.
├── .dockerignore
├── .env
├── docker-compose.yml
├── Dockerfile
├── main.py
├── requirements.txt
├── celery_app.py
├── tasks.py
└── README.md
```

## Documentação automática

Com a API rodando, acesse:
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`
- OpenAPI JSON: `http://127.0.0.1:8000/openapi.json`
