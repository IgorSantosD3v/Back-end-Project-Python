from celery_app import celery_app
import time

@celery_app.task(name="tasks.somar", bind=True)
def somar(self, a, b):
    time.sleep(3)  # Simula uma operação demorada
    return a + b

@celery_app.task(name="tasks.fatorial", bind=True)
def fatorial(self, n):
    time.sleep(3)  # Simula uma operação demorada
    if n < 0:
        raise ValueError("O número deve ser não-negativo.")

    resultado = 1
    for i in range(2, n + 1):
        resultado *= i

    return resultado  # Simula uma operação demorada