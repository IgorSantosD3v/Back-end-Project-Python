<div align="center">

# 📚 Livros API

**API REST para gerenciamento de livros**, construída com FastAPI e um stack completo de observabilidade e mensageria.

[![Python](https://img.shields.io/badge/Python-3.14-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![Kubernetes](https://img.shields.io/badge/Kubernetes-326CE5?logo=kubernetes&logoColor=white)](https://kubernetes.io/)
[![CI/CD](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-2088FF?logo=githubactions&logoColor=white)](https://github.com/features/actions)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](#-licença)

</div>

O projeto une CRUD, autenticação, processamento assíncrono, mensageria e logging estruturado em um ambiente containerizado, com pipeline de CI/CD e deploy em Kubernetes.

---

## 📑 Sumário

- [Funcionalidades](#-funcionalidades)
- [Stack utilizada](#️-stack-utilizada)
- [Arquitetura](#-arquitetura)
- [Estrutura do projeto](#-estrutura-do-projeto)
- [Variáveis de ambiente](#️-variáveis-de-ambiente)
- [Executando localmente](#-executando-localmente)
- [Executando com containers](#-executando-com-containers)
- [CI/CD (GitHub Actions)](#-cicd-github-actions)
- [Deploy no Kubernetes](#️-deploy-no-kubernetes)
- [Endpoints](#-endpoints)
- [Exemplos de uso](#-exemplos-de-uso)
- [Documentação automática](#-documentação-automática)
- [Troubleshooting](#-troubleshooting)
- [Licença](#-licença)

---

## ✨ Funcionalidades

- CRUD completo de livros com persistência SQLite
- Autenticação HTTP Basic nas rotas de livros
- Paginação na listagem de livros
- Demonstração de concorrência assíncrona com `asyncio`
- Processamento assíncrono com Celery + Redis
- Publicação de eventos no Kafka via `kafka-python`
- Envio de logs estruturados para Elasticsearch
- Visualização de logs em Kibana
- Pipeline de ingestão de logs com Logstash
- Execução local com Poetry e Docker Compose
- Pipeline GitHub Actions para testes, build e deploy em Kubernetes

---

## 🛠️ Stack utilizada

| Categoria | Tecnologias |
|---|---|
| Linguagem | Python 3.14 |
| API | FastAPI, Uvicorn |
| Banco de dados | SQLAlchemy 2.x, SQLite |
| Validação | Pydantic |
| Autenticação | HTTP Basic Auth |
| Assincronismo | `asyncio` |
| Tasks | Celery, Redis |
| Mensageria | Kafka, Zookeeper, Kafka UI |
| Observabilidade | Elasticsearch, Kibana, Logstash |
| Containerização | Docker, Docker Compose |
| Orquestração | Kubernetes (Minikube) |
| CI/CD | GitHub Actions |
| Dependências | Poetry |
| Testes | pytest, pytest-cov |

---

## 🏗️ Arquitetura

```
                 ┌──────────────┐
   Cliente ───▶  │   FastAPI    │ ───▶ SQLite (dados dos livros)
                 │  (main.py)   │
                 └──────┬───────┘
                         │
             ┌───────────┼────────────┐
             ▼                        ▼
      ┌─────────────┐         ┌──────────────┐
      │ Celery+Redis│         │ Kafka Producer│
      │ (tasks.py)  │         │(kafka_producer)│
      └─────────────┘         └──────┬───────┘
                                       ▼
                               ┌──────────────┐
                               │    Kafka     │
                               └──────┬───────┘
                                       ▼
                    ┌────────────────────────────────┐
                    │ Logstash ▶ Elasticsearch ▶ Kibana│
                    └────────────────────────────────┘
```

Todos os serviços rodam localmente via Docker Compose e, em produção, são orquestrados no Kubernetes (Minikube).

---

## 📁 Estrutura do projeto

```text
.
├── .dockerignore
├── .env
├── docker-compose.yml
├── Dockerfile
├── main.py
├── celery_app.py
├── tasks.py
├── kafka_producer.py
├── deployment.yaml
├── service.yaml
├── logging_config.yaml
├── logstash/
│   └── logstash.conf
├── .github/
│   └── workflows/
│       └── ci-cd.yml
├── pyproject.toml
├── poetry.lock
└── README.md
```

**Arquivos principais:**

| Arquivo | Responsabilidade |
|---|---|
| `main.py` | Aplicação FastAPI: modelos, rotas, autenticação, banco, Elasticsearch e Kafka |
| `tasks.py` | Tarefas Celery (`somar`, `fatorial`) |
| `celery_app.py` | Configuração do Celery com Redis broker/backend |
| `kafka_producer.py` | Produtor Kafka para enviar eventos de livro |
| `logging_config.yaml` | Configuração de logging local e em arquivo |
| `docker-compose.yml` | Orquestra os serviços do projeto |
| `Dockerfile` | Imagem da aplicação usando Poetry |
| `deployment.yaml` | Manifesto Kubernetes do Deployment |
| `service.yaml` | Manifesto Kubernetes do Service |
| `.github/workflows/ci-cd.yml` | Pipeline de CI/CD |

---

## ⚙️ Variáveis de ambiente

| Variável | Padrão | Descrição |
|---|---|---|
| `DATABASE_URL` | `sqlite:///./livros.db` | String de conexão do banco |
| `MEU_USUARIO` | `admin` | Usuário para HTTP Basic Auth |
| `MINHA_SENHA` | `admin` | Senha para HTTP Basic Auth |
| `REDIS_HOST` | `localhost` | Host Redis |
| `REDIS_PORT` | `6379` | Porta Redis |
| `KAFKA_SERVER` | `kafka:9092` | Broker Kafka para o app |
| `ELASTICSEARCH_URL` | `http://localhost:9200` | URL do Elasticsearch |
| `ELASTICSEARCH_INDEX` | `livros-logs` | Índice de logs no Elasticsearch |
| `LOG_FILE_PATH` | `undefined` | Caminho do log de arquivo quando usado no container |

> ⚠️ **Segurança:** as credenciais padrão (`admin`/`admin`) servem apenas para ambiente local. Nunca utilize esses valores em produção — defina `MEU_USUARIO` e `MINHA_SENHA` via secrets do orquestrador (Kubernetes Secret, GitHub Actions Secret, etc).

Exemplo de `.env`:

```env
MEU_USUARIO=admin
MINHA_SENHA=admin
DATABASE_URL=sqlite:///./livros.db
KAFKA_SERVER=kafka:9092
ELASTICSEARCH_URL=http://elasticsearch:9200
ELASTICSEARCH_INDEX=livros-logs
REDIS_HOST=redis
REDIS_PORT=6379
PYTHONUNBUFFERED=1
```

---

## 🚀 Executando localmente

### 1. Pré-requisitos

- Python 3.14+
- [Poetry](https://python-poetry.org/)
- Redis, Kafka e Elasticsearch acessíveis (localmente ou via `docker compose up -d redis kafka elasticsearch`)

### 2. Criar e ativar o ambiente virtual

**PowerShell (Windows):**

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install poetry
poetry install --no-root
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Linux / WSL:**

```bash
python -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip
python -m pip install poetry
poetry install --no-root
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

A API ficará disponível em `http://127.0.0.1:8000`.

### 3. Rodar os testes

```bash
pytest --cov
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
| Kibana | `http://127.0.0.1:5601` |
| Kafka UI | `http://127.0.0.1:8080` |
| Redis | `127.0.0.1:6379` |
| Elasticsearch | `http://127.0.0.1:9200` |
| Kafka broker (externo) | `127.0.0.1:9094` |

> ⚠️ **Observação:** internamente o Kafka usa `kafka:9092`, mas o `docker-compose` expõe a porta externa `9094`.

---

## 🔁 CI/CD (GitHub Actions)

A pipeline (`.github/workflows/ci-cd.yml`) roda em todo `push`/`pull_request` para `main`/`master`, ou manualmente via `workflow_dispatch`, e é composta por três jobs:

| Job | Runner | O que faz |
|---|---|---|
| **Testes e validação** | `ubuntu-latest` | Instala dependências com Poetry, valida `pyproject.toml` e roda `pytest` com cobertura |
| **Build e publicação da imagem Docker** | `ubuntu-latest` | Builda e publica a imagem no GHCR |
| **Deploy no Kubernetes** | `self-hosted` | Atualiza o manifesto e aplica os manifests no cluster |

O job de deploy usa um runner self-hosted conectado ao cluster local (necessário porque o Minikube só é acessível na máquina onde está rodando).

### Imagem publicada

As imagens ficam disponíveis no GitHub Container Registry:

```
ghcr.io/<owner>/backendproject:latest
ghcr.io/<owner>/backendproject:<sha>
```

---

## ☸️ Deploy no Kubernetes

O deploy é feito em um cluster local usando **Minikube**.

### Pré-requisitos na máquina do runner

- Docker instalado e em execução
- [Minikube](https://minikube.sigs.k8s.io/docs/start/) instalado
- `kubectl` configurado para o cluster Minikube
- Runner GitHub Actions com label `self-hosted`

### Subindo o cluster manualmente (se necessário)

```bash
minikube start --driver=docker
minikube status
kubectl get nodes
```

### Aplicando os manifests manualmente

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

---

## 📡 Endpoints

### Sem autenticação

| Método | Rota | Descrição |
|---|---|---|
| GET | `/` | Health check da API |
| GET | `/chamadas-externas` | Simula 3 chamadas assíncronas concorrentes |

### Tarefas em segundo plano (Celery)

| Método | Rota | Descrição |
|---|---|---|
| POST | `/calcular/soma` | Enfileira cálculo de soma |
| POST | `/calcular/fatorial` | Enfileira cálculo de fatorial |
| GET | `/tarefas/recentes` | Lista IDs e status das últimas tarefas |

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

---

## 🩺 Troubleshooting

| Sintoma | Causa provável | Solução |
|---|---|---|
| `connection refused` no deploy | Minikube não está rodando | `minikube start --driver=docker` |
| API sobe mas `/livros` retorna 401 | Credenciais erradas ou `.env` não carregado | Confirme `MEU_USUARIO`/`MINHA_SENHA` e se o `.env` está sendo lido |
| Kafka producer não conecta | Uso de `localhost:9092` fora do container | Use `kafka:9092` dentro da rede Docker, ou `127.0.0.1:9094` externamente |
| Logs não aparecem no Kibana | Logstash não processou o índice | Verifique `logstash/logstash.conf` e se o Elasticsearch está saudável (`/_cluster/health`) |
| Runner self-hosted não enxerga o cluster | Minikube roda em contexto isolado (ex: WSL) | Garanta que o runner esteja na mesma máquina/contexto onde o Minikube foi iniciado |

---

## 🤝 Contribuindo

Contribuições são bem-vindas. Para propor uma mudança:

1. Faça um fork do repositório
2. Crie uma branch (`git checkout -b feature/minha-feature`)
3. Commit suas alterações (`git commit -m 'feat: minha feature'`)
4. Push para a branch (`git push origin feature/minha-feature`)
5. Abra um Pull Request

---

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

<div align="center">

Desenvolvido por **Igor Santos** — [GitHub](https://github.com/IgorSantosD3v) · [LinkedIn](https://linkedin.com/in/igor-santos-7b993b357)

</div>