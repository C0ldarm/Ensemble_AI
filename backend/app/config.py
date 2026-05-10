import os
from dotenv import load_dotenv

load_dotenv()

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
WORKER_MODEL_1 = os.getenv("WORKER_MODEL_1")
WORKER_MODEL_2 = os.getenv("WORKER_MODEL_2")
ARBITER_MODEL = os.getenv("ARBITER_MODEL")