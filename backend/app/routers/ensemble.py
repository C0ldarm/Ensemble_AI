from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import List, Optional
import asyncio
import time

from app.core.workers.tasks import generate_with_model
from app.core.arbiter import AdvancedArbiter
from app.config import WORKER_MODEL_1, WORKER_MODEL_2

router = APIRouter()

class EnsembleRequest(BaseModel):
    prompt: str
    models: Optional[List[str]] = None

class EnsembleResponse(BaseModel):
    final_response: str
    used_models: List[str]
    method: str = "ensemble"
    raw_responses: Optional[List[dict]] = None
    execution_time_ms: Optional[int] = None
    arbiter_model: Optional[str] = None

@router.post("/ensemble", response_model=EnsembleResponse)
async def run_ensemble(request: EnsembleRequest):
    start_time = time.time()
    
    models = request.models or [WORKER_MODEL_1, WORKER_MODEL_2]
    
    tasks = [generate_with_model.delay(request.prompt, model) for model in models]
    raw_responses = await asyncio.to_thread(
        lambda: [task.get(timeout=180) for task in tasks]
    )
    
    arbiter = AdvancedArbiter()
    result = await arbiter.arbitrate(raw_responses, request.prompt)
    
    execution_time = int((time.time() - start_time) * 1000)
    
    return EnsembleResponse(
        final_response=result.get("final_response") or result.get("final_answer") or str(result),
        used_models=models,
        method=result.get("method", "ensemble"),
        raw_responses=raw_responses,
        execution_time_ms=execution_time,
        arbiter_model=result.get("arbiter_model")
    )