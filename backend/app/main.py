from fastapi import FastAPI
from app.routers import test_ensemble   # ← ВИПРАВЛЕНО

app = FastAPI(title="Ensemble AI - Stage 1")

app.include_router(test_ensemble.router, prefix="/api/v1", tags=["test"])

@app.get("/")
async def root():
    return {"message": "✅ Ensemble AI запущено! Stage 1 готовий. Перейди на /docs"}