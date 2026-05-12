from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import List, Optional
import asyncio
import time

from app.core.workers.tasks import generate_with_model
from app.core.arbiter import AdvancedArbiter
from app.config import WORKER_MODEL_1, WORKER_MODEL_2, ARBITER_MODEL

router = APIRouter()

class EnsembleRequest(BaseModel):
    prompt: str = Field(..., description="Запитання або промпт для ensemble")
    models: Optional[List[str]] = Field(
        default=None,
        description="Список моделей для worker'ів. Якщо не вказано — використовуються defaults",
        examples=[["qwen2.5:7b-instruct", "llama3.1:8b"]]
    )

class EnsembleResponse(BaseModel):
    final_response: str
    used_models: List[str]
    method: str
    raw_responses: List[dict] = None
    execution_time_ms: Optional[int] = None
    arbiter_model: Optional[str] = None

@router.post("/ensemble", response_model=EnsembleResponse)
async def run_ensemble(request: EnsembleRequest):
    start_time = time.time()
    
    # Якщо користувач не передав моделі — беремо з config
    models = request.models or [WORKER_MODEL_1, WORKER_MODEL_2]
    
    # Паралельний запуск
    tasks = [generate_with_model.delay(request.prompt, model) for model in models]
    raw_responses = await asyncio.to_thread(
        lambda: [task.get(timeout=120) for task in tasks]
    )
    
    # Advanced Arbiter
    arbiter = AdvancedArbiter()
    result = await arbiter.arbitrate(raw_responses, request.prompt)
    
    execution_time = int((time.time() - start_time) * 1000)
    
    return EnsembleResponse(
        final_response=result["final_response"],
        used_models=result["used_models"],
        method=result["method"],
        raw_responses=raw_responses,
        execution_time_ms=execution_time,
        arbiter_model=result.get("arbiter_model")
    )