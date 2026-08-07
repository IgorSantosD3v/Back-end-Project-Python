# 📚 API de Livros

API REST para gerenciamento de livros, construída com **FastAPI**, **SQLAlchemy**, **SQLite**, **Celery**, **Redis** e **Kafka**.

O projeto foi pensado como um estudo prático de arquitetura backend, unindo CRUD, autenticação, processamento assíncrono e mensageria em um único ambiente containerizado — com pipeline de CI/CD completa até o deploy em Kubernetes.

---

## ✨ Funcionalidades

- CRUD completo de livros
- Autenticação HTTP Basic nas rotas de livros
- Paginação na listagem
- Exemplo de concorrência assíncrona com `asyncio`
- Worker Celery usando Redis como broker/backend
- Broker Kafka com Zookeeper e interface Kafka UI
- Execução local via `venv` + `requirements.txt`
- Orquestração de containers com Docker Compose / Podman Compose
- Pipeline de CI/CD com GitHub Actions: testes → build/push da imagem → deploy em Kubernetes

---

## 🛠️ Stack utilizada

| Categoria | Tecnologias |
|---|---|
| Linguagem | Python `3.14` |
| API | FastAPI, Uvicorn (ASGI) |
| Dados | SQLAlchemy `2.x`, SQLite, Pydantic |
| Autenticação | HTTP Basic Auth |
| Assincronismo | `asyncio` |
| Tarefas em background | Celery + Redis |
| Mensageria | Kafka, Zookeeper, Kafka UI |
| Containerização | Docker / Podman, Docker Compose / Podman Compose |
| Orquestração | Kubernetes (minikube) |
| CI/CD | GitHub Actions (runner self-hosted) |
| Registro de imagens | GitHub Container Registry (GHCR) |
| Testes | pytest |
| Configuração | Arquivos `.env` |
| Documentação | Swagger, ReDoc, OpenAPI (gerados automaticamente pelo FastAPI) |

---

## 📁 Estrutura do projeto

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
├── deployment.yaml
├── service.yaml
├── .github
│   └── workflows
│       └── ci-cd.yml
└── README.md
```

**Arquivos principais:**

| Arquivo | Responsabilidade |
|---|---|
| `main.py` | Aplicação FastAPI: modelos, rotas, autenticação e banco |
| `tasks.py` | Tarefas Celery (`somar`, `fatorial`) |
| `celery_app.py` | Configuração do Celery com broker Redis |
| `kafka_producer.py` | Produtor simples para eventos Kafka |
| `Dockerfile` | Definição da imagem do container da API |
| `docker-compose.yml` | Orquestra `app`, `redis`, `celery`, `zookeeper`, `kafka` e `kafka-ui` |
| `requirements.txt` | Dependências Python do projeto |
| `.env` | Variáveis de ambiente da aplicação |
| `deployment.yaml` | Manifesto Kubernetes do Deployment da API |
| `service.yaml` | Manifesto Kubernetes do Service que expõe a API |
| `.github/workflows/ci-cd.yml` | Pipeline de CI/CD (testes, build/push, deploy) |

---

## ⚙️ Variáveis de ambiente

| Variável | Padrão | Descrição |
|---|---|---|
| `DATABASE_URL` | `sqlite:///./livros.db` | String de conexão do banco |
| `MEU_USUARIO` | `admin` | Usuário para HTTP Basic Auth |
| `MINHA_SENHA` | `admin` | Senha para HTTP Basic Auth |
| `KAFKA_SERVER` | `kafka:9092` | Endereço do broker Kafka |

Exemplo de `.env`:

```env
MEU_USUARIO=admin
MINHA_SENHA=admin
DATABASE_URL=sqlite:///./livros.db
KAFKA_SERVER=kafka:9092
PYTHONUNBUFFERED=1
```

---

## 🚀 Executando localmente

### 1. Criar e ativar o ambiente virtual

**PowerShell (Windows):**

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Linux / WSL:**

```bash
python -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

A API ficará disponível em `http://127.0.0.1:8000`.

### 2. Rodar os testes

```bash
pytest
```

---

## 🐳 Executando com containers

### Docker Compose

```bash
docker compose up -d --build
```

### Podman Compose (WSL recomendado)

```bash
cd /mnt/c/Users/Usuario/Desktop/Back-end-Project-Python
podman-compose up -d --build
```

### Parar os serviços

```bash
docker compose down
# ou
podman-compose down
```

### Verificar status dos containers

```bash
docker ps
# ou
podman ps
```

### Acessos após subir os containers

| Serviço | Endereço |
|---|---|
| API Swagger | `http://127.0.0.1:8000/docs` |
| Kafka UI | `http://127.0.0.1:8080` |
| Redis | `127.0.0.1:6379` |
| Kafka broker (externo) | `127.0.0.1:9094` |

> ⚠️ **Observação:** internamente o serviço Kafka usa `kafka:9092`, mas o `docker-compose` mapeia a porta externa para `9094`.

---

## 🔁 CI/CD (GitHub Actions)

A pipeline (`.github/workflows/ci-cd.yml`) roda em todo `push`/`pull_request` para `main`/`master`, ou manualmente via `workflow_dispatch`, e é composta por três jobs sequenciais:

| Job | Runner | O que faz |
|---|---|---|
| **Testes e validação** | `ubuntu-latest` | Instala dependências com Poetry, valida o `pyproject.toml` e roda `pytest` com relatório de cobertura (subindo um serviço Redis para os testes) |
| **Build e publicação da imagem Docker** | `ubuntu-latest` | Builda a imagem com Docker Buildx e publica no GHCR com as tags `latest` e `<sha do commit>` |
| **Deploy no Kubernetes** | `self-hosted` | Substitui a imagem no `deployment.yaml`, aplica os manifests (`deployment.yaml` + `service.yaml`) no cluster e aguarda o rollout |

Os dois primeiros jobs rodam em runners hospedados pelo GitHub. O job de deploy roda em um **runner self-hosted**, pois o cluster Kubernetes (minikube) usado neste projeto é local.

### Imagem publicada

As imagens ficam disponíveis no GitHub Container Registry:

```
ghcr.io/<owner>/backendproject:latest
ghcr.io/<owner>/backendproject:<sha>
```

---

## ☸️ Deploy no Kubernetes

O deploy é feito em um cluster **minikube** local, através do runner self-hosted configurado na máquina.

### Pré-requisitos na máquina do runner

- Docker instalado e em execução
- [minikube](https://minikube.sigs.k8s.io/docs/start/) instalado
- `kubectl` configurado apontando para o cluster do minikube
- Runner do GitHub Actions registrado no repositório com a label `self-hosted`

### Subindo o cluster manualmente (se necessário)

```bash
minikube start --driver=docker
minikube status
kubectl get nodes
```

### Aplicando os manifests manualmente (fora da pipeline)

```bash
kubectl apply -f deployment.yaml -n default
kubectl apply -f service.yaml -n default
kubectl rollout status deployment/livros-api --timeout=180s -n default
```

### Verificando o deploy

```bash
kubectl get pods -n default
kubectl get svc -n default
kubectl logs -l app=livros-api -n default
```

> 💡 **Dica:** se o job "Deploy no Kubernetes" falhar com `connection refused`, o cluster minikube provavelmente está parado. A pipeline já inclui um step que verifica e reinicia o minikube automaticamente antes de aplicar os manifests.

---

## 📡 Endpoints

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

---

## 💻 Exemplos de uso

**Verificar se a API está no ar:**

```bash
curl http://127.0.0.1:8000/
```

**Listar livros:**

```bash
curl -u admin:admin "http://127.0.0.1:8000/livros?page=1&limit=10"
```

**Adicionar livro:**

```bash
curl -u admin:admin -X POST "http://127.0.0.1:8000/adiciona" \
  -H "Content-Type: application/json" \
  -d '{"nome_livro":"Clean Code","autor_livro":"Robert C. Martin","ano_livro":2008}'
```

**Atualizar livro:**

```bash
curl -u admin:admin -X PUT "http://127.0.0.1:8000/atualiza/1" \
  -H "Content-Type: application/json" \
  -d '{"nome_livro":"Clean Code (2a edicao)","autor_livro":"Robert C. Martin","ano_livro":2009}'
```

**Deletar livro:**

```bash
curl -u admin:admin -X DELETE "http://127.0.0.1:8000/deletar/1"
```

---

## 📖 Documentação automática

Com a API em execução, acesse:

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`
- OpenAPI JSON: `http://127.0.0.1:8000/openapi.json`