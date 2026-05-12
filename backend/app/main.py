from fastapi import FastAPI
from app.routers import test_ensemble, ensemble   
from app.routers.ensemble_detailed import router as detailed_router

app = FastAPI(title="Ensemble AI - Stage 2")

app.include_router(test_ensemble.router, prefix="/api/v1", tags=["test"])
app.include_router(ensemble.router, prefix="/api/v1", tags=["ensemble"])
app.include_router(detailed_router, prefix="/api/v1", tags=["ensemble-detailed"])

@app.get("/")
async def root():
    return {"message": "✅ Ensemble AI Stage 2 запущено! /docs"}