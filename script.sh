#!/usr/bin/env bash
set -euo pipefail

DEPLOYMENT="deployment.yaml"
SERVICE="service.yaml"
DEPLOYMENT_NAME="livros-api"
SERVICE_NAME="livros-api-service"

find_command() {
    local cmd="$1"
    if command -v "$cmd" >/dev/null 2>&1; then
        echo "$cmd"
    elif command -v "${cmd}.exe" >/dev/null 2>&1; then
        echo "${cmd}.exe"
    else
        return 1
    fi
}

KUBECTL_BIN="$(find_command kubectl || true)"
MINIKUBE_BIN="$(find_command minikube || true)"

if [ -z "${KUBECTL_BIN:-}" ]; then
    echo "kubectl não foi encontrado. Instale-o no WSL ou no Windows e tente novamente."
    exit 1
fi

if [ -n "${MINIKUBE_BIN:-}" ]; then
    echo "Verificando se o Minikube está em execução..."
    if ! "$MINIKUBE_BIN" status | grep -q "Running"; then
        echo "Minikube não está em execução. Iniciando o Minikube..."
        "$MINIKUBE_BIN" start --driver=docker 2>/dev/null || "$MINIKUBE_BIN" start
    else
        echo "Minikube já está em execução."
    fi

    echo "Apontando o Docker CLI para o daemon interno do Minikube..."
    eval "$("$MINIKUBE_BIN" docker-env)"
else
    echo "Minikube não está instalado; tentando usar um cluster Kubernetes já disponível..."
    if ! "$KUBECTL_BIN" cluster-info >/dev/null 2>&1; then
        echo "Nenhum cluster Kubernetes foi encontrado. Inicie o Minikube ou um cluster existente."
        exit 1
    fi
fi

echo "Aplicando o deployment"
"$KUBECTL_BIN" apply -f "$DEPLOYMENT"

echo "Aplicando o service"
"$KUBECTL_BIN" apply -f "$SERVICE"

echo "Aguardando o deployment estar pronto..."
if ! "$KUBECTL_BIN" rollout status "deployment/$DEPLOYMENT_NAME" --timeout=180s; then
    echo "Deployment não ficou pronto. Verifique com:"
    echo "kubectl get pods"
    echo "kubectl describe deployment $DEPLOYMENT_NAME"
    echo "kubectl logs deployment/$DEPLOYMENT_NAME"
    exit 1
fi

echo "Iniciando port-forward para localhost:8000 -> service porta 80..."
"$KUBECTL_BIN" port-forward "svc/$SERVICE_NAME" 8000:80 >/tmp/livros-port-forward.log 2>&1 &

sleep 5

if command -v xdg-open >/dev/null 2>&1; then
    xdg-open http://localhost:8000
elif command -v powershell.exe >/dev/null 2>&1; then
    powershell.exe /c start http://localhost:8000
elif command -v cmd.exe >/dev/null 2>&1; then
    cmd.exe /c start http://localhost:8000
else
    echo "Não foi possível abrir o navegador automaticamente. Acesse http://localhost:8000 manualmente."
fi

echo "Aplicação está rodando em http://localhost:8000"
echo "Pressione Ctrl+C para encerrar o port-forward e sair do script."
wait