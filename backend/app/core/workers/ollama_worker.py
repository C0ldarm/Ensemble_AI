import httpx
from .base_worker import BaseWorker
from typing import Dict, Any
from app.config import OLLAMA_HOST

class OllamaWorker(BaseWorker):
    def __init__(self, model_name: str):
        self.model_name = model_name

    async def generate(self, prompt: str, model: str = None) -> Dict[str, Any]:
        model_to_use = model or self.model_name
        async with httpx.AsyncClient(timeout=1200.0) as client:
            response = await client.post(
                f"{OLLAMA_HOST}/api/generate",
                json={
                    "model": model_to_use,
                    "prompt": prompt,
                    "stream": False
                }
            )
            response.raise_for_status()
            data = response.json()
            return {
                "model": model_to_use,
                "response": data.get("response", ""),
                "done": data.get("done", False)
            }

    def get_model_name(self) -> str:
        return self.model_name