from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import test_ensemble, ensemble
from app.routers.ensemble_detailed import router as detailed_router
from app.routers.ensemble_custom import router as custom_router
import httpx
from fastapi.responses import JSONResponse
from fastapi import APIRouter

app = FastAPI(title="Ensemble AI - Stage 2")

# === CORS (дуже важливо для фронтенду) ===
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "*"],  # "*" для розробки
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Існуючі роутери
app.include_router(test_ensemble.router, prefix="/api/v1", tags=["test"])
app.include_router(ensemble.router, prefix="/api/v1", tags=["ensemble"])
app.include_router(detailed_router, prefix="/api/v1", tags=["ensemble-detailed"])
app.include_router(custom_router, prefix="/api/v1", tags=["ensemble-custom"])

# === Роутер моделей ===
models_router = APIRouter(prefix="/api/v1", tags=["models"])

@models_router.get("/models")
async def get_available_models():
    try:
        async with httpx.AsyncClient(timeout=100.0) as client:
            resp = await client.get("http://ollama:11434/api/tags")
            resp.raise_for_status()
            data = resp.json()
            models = [m["name"] for m in data.get("models", [])]
            return {"success": True, "models": models}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e), "models": []}
        )

app.include_router(models_router)

@app.get("/")
async def root():
    return {"message": "✅ Ensemble AI Stage 2 запущено! /docs"}