from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import List, Optional
import asyncio
from datetime import datetime
import uuid

from app.core.workers.tasks import generate_with_model
from app.core.arbiter import AdvancedArbiter
from app.config import WORKER_MODEL_1, WORKER_MODEL_2

router = APIRouter()

class DetailedEnsembleRequest(BaseModel):
    prompt: str
    models: Optional[List[str]] = None

class WorkerResponse(BaseModel):
    model: str
    response: str
    confidence: float = 0.7

class ArbiterInfo(BaseModel):
    final_response: str
    reasoning: str
    confidence: float = 0.85
    strategy: str = "advanced_synthesis"

class DetailedEnsembleResponse(BaseModel):
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    original_prompt: str
    workers: List[WorkerResponse]
    arbiter: ArbiterInfo
    execution_time_ms: int

@router.post("/ensemble/detailed", response_model=DetailedEnsembleResponse)
async def run_detailed_ensemble(request: DetailedEnsembleRequest):
    start_time = datetime.utcnow()
    
    models = request.models or [WORKER_MODEL_1, WORKER_MODEL_2]
    
    # Worker tasks
    tasks = [generate_with_model.delay(request.prompt, model) for model in models]
    raw_responses = await asyncio.to_thread(
        lambda: [task.get(timeout=120) for task in tasks]
    )

    # Arbiter
    arbiter = AdvancedArbiter()
    arbiter_result = await arbiter.arbitrate(raw_responses, request.prompt)

    execution_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)

    return DetailedEnsembleResponse(
        original_prompt=request.prompt,
        workers=[
            WorkerResponse(model=r["model"], response=r["response"])
            for r in raw_responses
        ],
        arbiter=ArbiterInfo(
            final_response=arbiter_result.get("final_response", ""),
            reasoning=arbiter_result.get("reasoning", "Арбітр синтезував відповідь"),
            confidence=0.85
        ),
        execution_time_ms=execution_time
    )