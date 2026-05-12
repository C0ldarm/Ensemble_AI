from app.celery_app import celery_app
from app.core.workers.ollama_worker import OllamaWorker
import asyncio

@celery_app.task(name="generate_with_model")
def generate_with_model(prompt: str, model: str):
    """Синхронна Celery task"""
    worker = OllamaWorker(model)
    # Запускаємо async generate всередині task
    return asyncio.run(worker.generate(prompt))