from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_calcular_soma(mocker):
    mock_somar_delay = mocker.patch("tasks.somar.delay")
    mock_redis_lpush = mocker.patch("main.redis_client.lpush")
    mock_redis_ltrim = mocker.patch("main.redis_client.ltrim")

    mock_somar_delay.return_value.id = "fake_task_id"

    response = client.post("/calcular/soma", params={"a": 2, "b": 3})
    assert response.status_code == 200
    assert response.json() == {
        "task_id": "fake_task_id",
        "message": "A soma está sendo processada em segundo plano. Use o task_id para verificar o status."
        }

    mock_redis_lpush.assert_called_once()
    mock_redis_ltrim.assert_called_once()

def test_calcular_fatorial(mocker):
    mock_fatorial_delay = mocker.patch("tasks.fatorial.delay")
    mock_redis_lpush = mocker.patch("main.redis_client.lpush")
    mock_redis_ltrim = mocker.patch("main.redis_client.ltrim")

    mock_fatorial_delay.return_value.id = "fake_task_id"

    response = client.post("/calcular/fatorial", params={"n": 5})
    assert response.status_code == 200
    assert response.json() == {
        "task_id": "fake_task_id",
        "message": "O cálculo do fatorial está sendo processado em segundo plano. Use o task_id para verificar o status."
        }

    mock_redis_lpush.assert_called_once()
    mock_redis_ltrim.assert_called_once()
    