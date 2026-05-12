from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseWorker(ABC):
    @abstractmethod
    async def generate(self, prompt: str, model: str = None) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_model_name(self) -> str:
        pass