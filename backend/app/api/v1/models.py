# backend/app/api/v1/models.py
from fastapi import APIRouter
import requests

router = APIRouter(prefix="/api/v1", tags=["models"])

@router.get("/models")
async def get_available_models():
    try:
        resp = requests.get("http://ollama:11434/api/tags", timeout=5)
        resp.raise_for_status()
        data = resp.json()
        models = [model["name"] for model in data.get("models", [])]
        return {"models": models, "success": True}
    except Exception as e:
        return {"models": [], "success": False, "error": str(e)}