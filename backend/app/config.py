import os
from dotenv import load_dotenv

load_dotenv()

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://ollama:11434")
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

# === Worker моделі (виконують первинну генерацію) ===
WORKER_MODEL_1 = os.getenv("WORKER_MODEL_1", "qwen2.5:7b-instruct")
WORKER_MODEL_2 = os.getenv("WORKER_MODEL_2", "llama3.1:8b")

# === Arbiter модель (синтезує фінальну відповідь) ===
ARBITER_MODEL = os.getenv("ARBITER_MODEL", "qwen2.5:14b-arbiter")

# System prompt для арбітра
ARBITER_SYSTEM_PROMPT = """Ти — арбітр Ensemble AI. Твоє завдання — синтезувати відповіді кількох моделей в одну фінальну.

Пріоритети (від найважливішого):
1. Фактична точність і логічна коректність
2. Повнота (включати корисні деталі з різних відповідей)
3. Природність і стиль (відповідати в тому ж регістрі, що й запит)
4. Граматика і чистота мови

Заборонено:
- Повністю копіювати будь-яку з відповідей
- Додавати meta-коментарі ("як арбітр...", "моделі сказали...")
- Вигадувати факти, яких немає в жодній відповіді
- Ігнорувати явні помилки в оригінальних відповідях"""