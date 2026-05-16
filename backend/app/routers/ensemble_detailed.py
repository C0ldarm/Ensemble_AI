from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import List, Optional
import asyncio
from datetime import datetime
import uuid

from app.core.workers.tasks import generate_with_model
from app.core.arbiter import AdvancedArbiter

router = APIRouter()

class DetailedEnsembleRequest(BaseModel):
    prompt: str
    models: Optional[List[str]] = None
    arbiter_prompt: Optional[str] = None
    arbiter_model: Optional[str] = None

class WorkerResponse(BaseModel):
    model: str
    answer: str
    confidence: float = 0.7

class ArbiterInfo(BaseModel):
    model: str
    prompt_used: Optional[str] = None
    final_answer: str
    reasoning: str
    strategy: str = "advanced_synthesis"
    confidence: float = 0.85
    selected_from: List[str] = []

class DetailedEnsembleResponse(BaseModel):
    schema_version: str = "3.0"
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    original_query: str
    workers: List[WorkerResponse]
    arbiter: ArbiterInfo
    execution_time_ms: int

@router.post("/ensemble/detailed", response_model=DetailedEnsembleResponse)
async def run_detailed_ensemble(request: DetailedEnsembleRequest):
    start_time = datetime.utcnow()
    
    models = request.models or []  # якщо не передали — будемо брати defaults у worker'ах, але краще завжди передавати з фронту

    # Worker tasks
    tasks = [generate_with_model.delay(request.prompt, model) for model in models]
    raw_responses = await asyncio.to_thread(
        lambda: [task.get(timeout=180) for task in tasks]
    )

    # Arbiter
    arbiter = AdvancedArbiter()
    arbiter_result = await arbiter.arbitrate(
        responses=raw_responses,
        prompt=request.prompt,
        arbiter_prompt=request.arbiter_prompt,
        arbiter_model=request.arbiter_model
    )

    execution_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)

    return DetailedEnsembleResponse(
        original_query=request.prompt,
        workers=[
            WorkerResponse(
                model=r.get("model", "unknown"),
                answer=r.get("response", ""),
                confidence=r.get("confidence", 0.7)
            )
            for r in raw_responses
        ],
        arbiter=ArbiterInfo(
            model=arbiter_result.get("arbiter_model", request.arbiter_model or "unknown"),
            prompt_used=arbiter_result.get("prompt_used") or request.arbiter_prompt,
            final_answer=arbiter_result.get("final_response") or arbiter_result.get("final_answer", ""),
            reasoning=arbiter_result.get("reasoning", ""),
            strategy=arbiter_result.get("strategy", "advanced_synthesis"),
            confidence=arbiter_result.get("confidence", 0.85),
            selected_from=[r.get("model") for r in raw_responses if "model" in r]
        ),
        execution_time_ms=execution_time
    )