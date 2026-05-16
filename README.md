# Ensemble AI

Система паралельної генерації відповідей кількома LLM-моделями з інтелектуальним арбітром.

## Опис

Ensemble AI — це MVP-рішення, яке дозволяє запускати кілька LLM-моделей паралельно, збирати їхні відповіді та використовувати потужний арбітр (Advanced Arbiter) для синтезу найкращої фінальної відповіді.

Проєкт розроблений для демонстрації переваг ensemble-підходу над використанням однієї моделі.

## Стек технологій

### Backend
- **FastAPI** — основний фреймворк
- **Celery + Redis** — паралельна обробка запитів
- **Ollama** — локальний запуск LLM-моделей
- **Advanced Arbiter** — інтелектуальний синтез відповідей
- **Docker Compose** — оркестрація всіх сервісів

### Frontend
- **Next.js 15** (App Router)
- **TypeScript**
- **Tailwind CSS**
- **Axios**

## Основні можливості

- Динамічний вибір моделей з Ollama
- Режими: Standard, Detailed, Custom
- Кастомний промпт і вибір моделі-арбітра
- Згортання/розгортання бокової панелі
- Збереження налаштувань і відповідей у JSON
- Детальний лог роботи (workers + reasoning арбітра)

## Як запустити проєкт

### 1. Клонування репозиторію

```bash
git clone https://github.com/C0ldarm/Ensemble_AI.git
cd Ensemble_AI
```

## Як запустити проєкт

1. Клонування репозиторію

```bash
git clone https://github.com/C0ldarm/Ensemble_AI.git
cd Ensemble_AI
```

далі скачування моделей

2. Запуск через Docker Compose (рекомендований спосіб)

```bash
docker-compose up --build -d
```

3. Відкриття сервісів

```bash
- Frontend: http://localhost:3000
- Backend (Swagger): http://localhost:8000/docs
- Ollama: http://localhost:11434
```

4. Локальний запуск фронтенду (для розробки)

```bash
cd frontend
npm install
npm run dev
```

## Структура проєкту

```bash
Ensemble_AI/
├── backend/              # FastAPI + Celery + Arbiter
├── frontend/             # Next.js 15
├── docker-compose.yml
├── README.md
└── Stage_*.md            # документація по етапах
```

## Основні ендпоінти API

- GET /api/v1/models — список доступних моделей в Ollama
- POST /api/v1/ensemble — стандартний режим
- POST /api/v1/ensemble/detailed — детальний режим з reasoning