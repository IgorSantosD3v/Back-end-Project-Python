Atualizei o README com uma visão mais completa da stack e das tecnologias do projeto.

```markdown
# API de Livros

API REST para gerenciamento de livros com FastAPI, SQLAlchemy, SQLite, Celery, Redis e Kafka.

O projeto implementa:
- CRUD completo de livros
- autenticação HTTP Basic nas rotas de livros
- paginação na listagem
- exemplo de concorrência assíncrona com `asyncio`
- execução local com `venv` e `requirements.txt`
- orquestração de containers com Docker Compose / Podman Compose
- worker Celery usando Redis
- broker Kafka com Zookeeper e interface Kafka UI

## Tecnologias presentes

Esta aplicação utiliza uma stack completa de backend com foco em API REST, banco de dados relacional, fila de tarefas, mensageria e containerização:

- Python `3.14`
- FastAPI para criação da API REST
- Uvicorn como servidor ASGI
- SQLAlchemy `2.x` como ORM
- SQLite como banco de dados local
- Pydantic para validação de dados
- HTTP Basic Auth para autenticação das rotas de livros
- `asyncio` para execução de chamadas assíncronas
- Celery para processamento assíncrono de tarefas
- Redis como broker/resultado para Celery
- Kafka como broker de eventos
- Zookeeper como coordenador do Kafka
- Kafka UI para visualização e inspeção do cluster Kafka
- Docker / Podman para containerização
- Docker Compose / Podman Compose para orquestração dos serviços
- pytest para execução de testes
- Arquivos `.env` para configuração por variáveis de ambiente
- Swagger / ReDoc / OpenAPI gerados automaticamente pelo FastAPI

## Arquivos principais

- `main.py`: aplicação FastAPI, modelos, rotas, autenticação e banco
- `tasks.py`: tarefas Celery (`somar`, `fatorial`)
- `celery_app.py`: configuração do Celery com broker Redis
- `kafka_producer.py`: produtor simples para eventos Kafka
- `Dockerfile`: define a imagem do container da API
- `docker-compose.yml`: orquestra `app`, `redis`, `celery`, `zookeeper`, `kafka` e `kafka-ui`
- `requirements.txt`: dependências Python usadas no projeto
- `.env`: variáveis de ambiente para a aplicação

## Variáveis de ambiente

Variáveis lidas pela aplicação:
- `DATABASE_URL` — padrão: `sqlite:///./livros.db`
- `MEU_USUARIO` — padrão: `admin`
- `MINHA_SENHA` — padrão: `admin`
- `KAFKA_SERVER` — padrão: `kafka:9092`

Exemplo de `.env`:

```env
MEU_USUARIO=admin
MINHA_SENHA=admin
DATABASE_URL=sqlite:///./livros.db
KAFKA_SERVER=kafka:9092
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

### Criar e ativar `venv`

No PowerShell (Windows):

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

### Executar testes

```bash
pytest
```

## Execução com containers

### Docker Compose

```bash
docker compose up -d --build
```

### Podman Compose (WSL recomendado)

```bash
cd /mnt/c/Users/Usuario/Desktop/Back-end-Project-Python
podman-compose up -d --build
```

Para parar os serviços:

```bash
docker compose down
# ou
podman-compose down
```

### Verificar status

```bash
docker ps
# ou
podman ps
```

### Acessos após subir os containers

- API Swagger: `http://127.0.0.1:8000/docs`
- Kafka UI: `http://127.0.0.1:8080`
- Redis: `127.0.0.1:6379`
- Kafka broker (externo): `127.0.0.1:9094`

> Observação: internamente o serviço Kafka pode usar `kafka:9092`, mas o mapeamento externo no `docker-compose` expõe `9094`.

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
├── kafka_producer.py
└── README.md
```

## Documentação automática

Com a API rodando, acesse:
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`
- OpenAPI JSON: `http://127.0.0.1:8000/openapi.json`
