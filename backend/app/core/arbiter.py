import httpx
from typing import List, Dict, Any
from app.config import OLLAMA_HOST, ARBITER_SYSTEM_PROMPT

print(f"[ARBITER] Using model: qwen2.5:14b-arbiter")

class AdvancedArbiter:
    async def arbitrate(self, responses: List[Dict[str, Any]], prompt: str) -> Dict[str, Any]:
        if not responses:
            return {"error": "No responses"}

        context = "\n\n".join([
            f"Модель {r['model']} відповіла: {r['response']}"
            for r in responses
        ])

        arbiter_prompt = f"""Запит користувача:
            {prompt}

            Відповіді моделей:
            {context}

            Інструкція:
            - Якщо відповіді доповнюють одна одну — об'єднай найкращі частини
            - Якщо суперечать — обери більш точну/конкретну або вкажи на розбіжність
            - Виправляй граматичні та стилістичні помилки
            - Відповідай у тому ж стилі, що й запит (коротко — коротко)

            ФІНАЛЬНА ВІДПОВІДЬ: [тільки відповідь користувачу, без будь-яких префіксів]
            ПОЯСНЕННЯ: [1-2 речення: що саме взяв, чому, і що виправив]"""

        async with httpx.AsyncClient(timeout=180.0) as client:
            response = await client.post(
                f"{OLLAMA_HOST}/api/generate",
                json={
                    "model": "qwen2.5:14b-arbiter",
                    "prompt": arbiter_prompt,
                    "system": ARBITER_SYSTEM_PROMPT,
                    "stream": False,
                    "options": {"temperature": 0.6, "top_p": 0.95}
                }
            )
            response.raise_for_status()
            data = response.json()
            
            full_text = data.get("response", "").strip()
            
            # Розділяємо фінальну відповідь і reasoning
            if "ПОЯСНЕННЯ:" in full_text:
                final, reasoning = full_text.split("ПОЯСНЕННЯ:", 1)
                final = final.replace("ФІНАЛЬНА ВІДПОВІДЬ:", "").strip()
                reasoning = reasoning.strip()
            else:
                final = full_text
                reasoning = "Арбітр синтезував відповідь на основі аналізу моделей."

            return {
                "final_response": final,
                "reasoning": reasoning,
                "strategy": "advanced_synthesis",
                "confidence": round(0.75 + (0.2 * len(responses) / 3), 2),  # динамічний
            }