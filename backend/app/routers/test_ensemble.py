from fastapi import APIRouter, Body
from pydantic import BaseModel
import httpx
from app.config import OLLAMA_HOST, WORKER_MODEL_1, WORKER_MODEL_2

router = APIRouter()

class EnsembleRequest(BaseModel):
    prompt: str

@router.post("/test-ensemble")
async def test_ensemble(request: EnsembleRequest = Body(...)):
    if not WORKER_MODEL_1 or not WORKER_MODEL_2:
        return {"error": "Моделі не завантажені з .env — перевір docker-compose.yml"}

    async with httpx.AsyncClient(timeout=120.0) as client:
        try:
            # Worker 1
            resp1 = await client.post(
                f"{OLLAMA_HOST}/api/generate",
                json={"model": WORKER_MODEL_1, "prompt": request.prompt, "stream": False}
            )
            resp1.raise_for_status()
            answer1 = resp1.json().get("response", "No response")

            # Worker 2 — review + покращення
            review_prompt = f"Перевір і покращ цю відповідь:\n{answer1}\n\nОригінальний запит: {request.prompt}"
            resp2 = await client.post(
                f"{OLLAMA_HOST}/api/generate",
                json={"model": WORKER_MODEL_2, "prompt": review_prompt, "stream": False}
            )
            resp2.raise_for_status()
            final_answer = resp2.json().get("response", "No response")

            return {
                "worker1_model": WORKER_MODEL_1,
                "worker1": answer1,
                "worker2_model": WORKER_MODEL_2,
                "worker2_review": final_answer,
                "final": final_answer
            }

        except Exception as e:
            return {"error": str(e), "details": "Перевір, чи моделі завантажені в Ollama (ollama list)"}