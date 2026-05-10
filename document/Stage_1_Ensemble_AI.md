# Stage 1: Ensemble AI - Progress Report

### Що зроблено

- GitHub: репозиторій `C0ldarm/Ensemble_AI` активовано, створено повну структуру проєкту, зроблено перший коміт Stage 1 і пуш в `origin main`
- Docker Compose: повністю запущений стек Stage 1
  - `postgres:16-alpine`
  - `ollama/ollama:latest` (з підтримкою NVIDIA RTX A1000 6GB + CUDA)
  - `fastapi` (Python 3.12 + uvicorn)
- Ollama: контейнер запущений, GPU розпізнано, завантажено моделі:
  - `qwen2.5:7b-instruct`
  - `phi3:mini`
- FastAPI Skeleton (Orchestrator):
  - `backend/app/main.py`
  - `backend/app/config.py`
  - `backend/app/routers/test_ensemble.py`
- Реалізовано тестовий ендпоінт `/api/v1/test-ensemble` — працює взаємодія між двома моделями (Worker1 → Worker2 review)
- Платформа запущена локально: http://localhost:8000/docs (Swagger UI доступний)
- Моделі повністю кастомні — задаються тільки через `.env` (ніяких hardcoded)

### Поточний технологічний стек (Stage 1)

- **Inference Engine**: Ollama (Docker + GPU)
- **Orchestrator**: FastAPI + httpx (асинхронні запити)
- **Database**: PostgreSQL 16
- **Containerization**: Docker Compose v3.9
- **Моделі**: легкі (3B–7B) для швидкого тестування
- **Взаємодія**: послідовна (Worker1 → Worker2) — заготовка під паралельність

### Структура проєкту (на момент завершення Stage 1)

```bash
Ensemble_AI/
├── .env
├── docker-compose.yml
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── main.py
│       ├── config.py
│       └── routers/
│           └── test_ensemble.py