from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import List, Optional, Literal
import asyncio
from datetime import datetime
import uuid
import logging

from app.core.workers.tasks import generate_with_model
from app.core.arbiter import AdvancedArbiter

router = APIRouter()
logger = logging.getLogger(__name__)

class CustomEnsembleRequest(BaseModel):
    prompt: str
    models: List[str]
    strategy: Literal["majority", "argumentation", "consensus"] = "majority"
    arbiter_model: Optional[str] = None
    arbiter_prompt: Optional[str] = None
    allow_follow_up_requests: bool = False

class WorkerResponse(BaseModel):
    model: str
    answer: str
    confidence: float = 0.7

class ArbiterInfo(BaseModel):
    model: str
    final_answer: str
    reasoning: str
    strategy: str
    confidence: float
    consensus_info: Optional[dict] = None

class ConversationEntry(BaseModel):
    type: str
    details: dict

class CustomEnsembleResponse(BaseModel):
    schema_version: str = "3.0"
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    mode: str = "custom"
    original_query: str
    strategy: str
    workers: List[WorkerResponse]
    arbiter: ArbiterInfo
    conversation_history: List[dict]
    execution_time_ms: int

@router.post("/ensemble/custom", response_model=CustomEnsembleResponse)
async def run_custom_ensemble(request: CustomEnsembleRequest):
    start_time = datetime.utcnow()
    
    logger.info(f"[CUSTOM ENSEMBLE] Запуск з стратегією: {request.strategy}")
    logger.info(f"[CUSTOM ENSEMBLE] Моделі: {request.models}")
    logger.info(f"[CUSTOM ENSEMBLE] Арбітр: {request.arbiter_model}")
    
    try:
        # Worker tasks
        tasks = [generate_with_model.delay(request.prompt, model) for model in request.models]
        raw_responses = await asyncio.to_thread(
            lambda: [task.get(timeout=300) for task in tasks]
        )
        
        logger.info(f"[CUSTOM ENSEMBLE] Отримано {len(raw_responses)} відповідей від моделей")

        # Arbiter with strategy
        arbiter = AdvancedArbiter()
        arbiter_result = await arbiter.arbitrate_with_strategy(
            responses=raw_responses,
            prompt=request.prompt,
            strategy=request.strategy,
            arbiter_model=request.arbiter_model,
            arbiter_prompt=request.arbiter_prompt,
            allow_follow_ups=request.allow_follow_up_requests,
        )
        
        logger.info(f"[CUSTOM ENSEMBLE] Арбітр завершив роботу")

        execution_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
        
        logger.info(f"[CUSTOM ENSEMBLE] Загальний час: {execution_time}ms")

        return CustomEnsembleResponse(
            original_query=request.prompt,
            strategy=request.strategy,
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
                final_answer=arbiter_result.get("final_response", ""),
                reasoning=arbiter_result.get("reasoning", ""),
                strategy=arbiter_result.get("strategy", request.strategy),
                confidence=arbiter_result.get("confidence", 0.75),
                consensus_info=arbiter_result.get("consensus_info")
            ),
            conversation_history=arbiter_result.get("conversation_history", []),
            execution_time_ms=execution_time
        )
    
    except Exception as e:
        logger.error(f"[CUSTOM ENSEMBLE] Помилка: {str(e)}", exc_info=True)
        raise
