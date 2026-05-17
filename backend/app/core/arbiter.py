import httpx
import logging
from typing import List, Dict, Any
from difflib import SequenceMatcher
from app.config import (
    OLLAMA_HOST,
    ARBITER_SYSTEM_PROMPT,
    STRATEGY_MAJORITY_SYSTEM_PROMPT,
    STRATEGY_ARGUMENTATION_SYSTEM_PROMPT,
    STRATEGY_CONSENSUS_SYSTEM_PROMPT,
    FOLLOW_UP_REQUEST_TEMPLATE
)

# === Logging ===
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

print(f"[ARBITER] Ready. Default model: qwen2.5:14b-arbiter")

class AdvancedArbiter:
    async def arbitrate(
        self,
        responses: List[Dict[str, Any]],
        prompt: str,
        arbiter_prompt: str | None = None,
        arbiter_model: str | None = None,
    ) -> Dict[str, Any]:
        """Базовий метод арбітрації (дефолтний режим)"""
        if not responses:
            return {"error": "No responses"}

        # Якщо користувач не передав свій промпт — використовуємо дефолтний
        user_prompt = arbiter_prompt or f"""Запит користувача:
{prompt}

Відповіді моделей:
{"\n\n".join([f"Модель {r['model']} відповіла: {r['response']}" for r in responses])}

Інструкція:
- Якщо відповіді доповнюють одна одну — об'єднай найкращі частини
- Якщо суперечать — обери більш точну/конкретну або вкажи на розбіжність
- Виправляй граматичні та стилістичні помилки
- Відповідай у тому ж стилі, що й запит

ФІНАЛЬНА ВІДПОВІДЬ: [тільки відповідь користувачу, без префіксів]
ПОЯСНЕННЯ: [1-2 речення: що саме взяв, чому, і що виправив]"""

        # Якщо користувач не передав модель арбітра — використовуємо дефолтну
        model = arbiter_model or "qwen2.5:14b-arbiter"

        async with httpx.AsyncClient(timeout=300.0) as client:
            response = await client.post(
                f"{OLLAMA_HOST}/api/generate",
                json={
                    "model": model,
                    "prompt": user_prompt,
                    "system": ARBITER_SYSTEM_PROMPT,
                    "stream": False,
                    "options": {"temperature": 0.6, "top_p": 0.95}
                }
            )
            response.raise_for_status()
            data = response.json()

            full_text = data.get("response", "").strip()

            # Розділяємо фінальну відповідь і пояснення
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
                "arbiter_model": model,
                "confidence": round(0.75 + (0.2 * len(responses) / 3), 2),
            }

    async def arbitrate_with_strategy(
        self,
        responses: List[Dict[str, Any]],
        prompt: str,
        strategy: str = "majority",
        arbiter_model: str | None = None,
        arbiter_prompt: str | None = None,
        allow_follow_ups: bool = False,
    ) -> Dict[str, Any]:
        """
        Арбітрація з вибором стратегії
        
        Стратегії:
        - majority: вибір більшості
        - argumentation: найбільш аргументована
        - consensus: консенсус з follow-ups при конфліктах
        """
        if not responses:
            return {"error": "No responses"}

        model = arbiter_model or "qwen2.5:14b-arbiter"
        conversation_history = []  # Логування діалогу для JSON

        if strategy == "majority":
            return await self._arbitrate_majority(
                responses, prompt, model, arbiter_prompt, conversation_history
            )
        elif strategy == "argumentation":
            return await self._arbitrate_argumentation(
                responses, prompt, model, arbiter_prompt, conversation_history
            )
        elif strategy == "consensus":
            return await self._arbitrate_consensus(
                responses, prompt, model, arbiter_prompt, allow_follow_ups, conversation_history
            )
        else:
            return await self.arbitrate(responses, prompt, arbiter_prompt, model)

    async def _arbitrate_majority(
        self,
        responses: List[Dict[str, Any]],
        prompt: str,
        model: str,
        custom_prompt: str | None,
        conversation_history: List[Dict],
    ) -> Dict[str, Any]:
        """Стратегія БІЛЬШОСТІ"""
        logger.info(f"[MAJORITY] Порахування голосів: {len(responses)} моделей")
        
        # Визначаємо поріг
        total_models = len(responses)
        threshold = 2 if total_models == 3 else max(3, (total_models // 2) + 1)
        
        logger.info(f"[MAJORITY] Поріг консенсусу: {threshold} з {total_models}")

        # Рахуємо однакові відповіді
        response_counts = {}
        for r in responses:
            resp_text = r.get("response", "").strip()
            if resp_text not in response_counts:
                response_counts[resp_text] = []
            response_counts[resp_text].append(r.get("model", "unknown"))

        # Сортуємо за кількістю голосів
        sorted_responses = sorted(
            response_counts.items(), key=lambda x: len(x[1]), reverse=True
        )

        # Логування
        for resp_text, models in sorted_responses:
            logger.info(f"[MAJORITY] {len(models)} моделей: {models[:2]}... ({len(resp_text)} символів)")

        # Перевіряємо консенсус
        if sorted_responses and len(sorted_responses[0][1]) >= threshold:
            # Консенсус досягнут!
            majority_response = sorted_responses[0][0]
            majority_models = sorted_responses[0][1]
            
            logger.info(f"[MAJORITY] Консенсус достигнут! {len(majority_models)} моделей обрали одну версію")
            conversation_history.append({
                "type": "majority_decision",
                "consensus_reached": True,
                "voting_models": majority_models,
                "votes": len(majority_models),
                "threshold": threshold
            })

            return {
                "final_response": majority_response,
                "reasoning": f"Консенсус: {len(majority_models)} з {len(responses)} моделей обрали одну відповідь",
                "strategy": "majority",
                "arbiter_model": model,
                "confidence": round(len(majority_models) / len(responses), 2),
                "conversation_history": conversation_history,
                "consensus_info": {
                    "consensus_reached": True,
                    "voting_models": majority_models,
                    "dissenting_models": [m["model"] for m in responses if m["model"] not in majority_models]
                }
            }
        else:
            # Немає консенсусу - синтезуємо
            logger.info(f"[MAJORITY] Консенсусу немає. Синтезування...")
            return await self._synthesize_responses(
                responses, prompt, model, custom_prompt, "majority", conversation_history
            )

    async def _arbitrate_argumentation(
        self,
        responses: List[Dict[str, Any]],
        prompt: str,
        model: str,
        custom_prompt: str | None,
        conversation_history: List[Dict],
    ) -> Dict[str, Any]:
        """Стратегія АРГУМЕНТОВАНОСТІ"""
        logger.info(f"[ARGUMENTATION] Аналіз якості аргументації {len(responses)} моделей")

        user_prompt = custom_prompt or f"""Запит користувача:
{prompt}

Відповіді моделей:
{"\n\n".join([f"Модель {r['model']}:\\n{r['response']}" for r in responses])}

Проаналізуй якість аргументації кожної відповіді і обери найкращу.
Критерії: фактичність, логічність, деталізація, обґрунтованість.

ОБРАНА ВЕРСІЯ: [текст найкращої відповіді]
МОДЕЛЬ: [яка модель]
ЯКІСТЬ АРГУМЕНТІВ: [детальний аналіз]
ПОЯСНЕННЯ: [чому саме ця версія найкраща]"""

        async with httpx.AsyncClient(timeout=300.0) as client:
            response = await client.post(
                f"{OLLAMA_HOST}/api/generate",
                json={
                    "model": model,
                    "prompt": user_prompt,
                    "system": STRATEGY_ARGUMENTATION_SYSTEM_PROMPT,
                    "stream": False,
                    "options": {"temperature": 0.7, "top_p": 0.95}
                }
            )
            response.raise_for_status()
            data = response.json()

        full_text = data.get("response", "").strip()
        logger.info(f"[ARGUMENTATION] Арбітр обрав версію на основі аргументації")

        conversation_history.append({
            "type": "argumentation_analysis",
            "arbiter_decision": full_text[:200]
        })

        # Парсимо відповідь
        result = {
            "final_response": full_text,
            "reasoning": "Обрана версія з найкращою аргументацією",
            "strategy": "argumentation",
            "arbiter_model": model,
            "confidence": 0.82,
            "conversation_history": conversation_history,
        }

        return result

    async def _arbitrate_consensus(
        self,
        responses: List[Dict[str, Any]],
        prompt: str,
        model: str,
        custom_prompt: str | None,
        allow_follow_ups: bool,
        conversation_history: List[Dict],
    ) -> Dict[str, Any]:
        """Стратегія КОНСЕНСУСУ з можливими follow-ups"""
        logger.info(f"[CONSENSUS] Аналіз конфліктів: {len(responses)} моделей")

        # Крок 1: Виявляємо конфлікти
        conflicts = self._detect_conflicts(responses)
        
        if not conflicts:
            logger.info(f"[CONSENSUS] Конфліктів не виявлено")
            conversation_history.append({
                "type": "consensus_check",
                "conflicts_found": False,
            })
            # Немає конфліктів - повертаємо відповіді як є
            return {
                "final_response": responses[0].get("response", ""),
                "reasoning": "Немає конфліктів - всі моделі согласні",
                "strategy": "consensus",
                "arbiter_model": model,
                "confidence": 0.9,
                "conversation_history": conversation_history,
                "consensus_info": {
                    "conflicts_found": False,
                }
            }

        logger.info(f"[CONSENSUS] Виявлено {len(conflicts)} конфліктів")
        conversation_history.append({
            "type": "consensus_check",
            "conflicts_found": True,
            "conflict_count": len(conflicts),
        })

        # Крок 2: Якщо allow_follow_ups - запрошуємо обґрунтування
        follow_up_data = {}
        if allow_follow_ups:
            logger.info(f"[CONSENSUS] Запит обґрунтувань у конфліктних моделей")
            follow_up_data = await self._request_follow_ups(
                conflicts, responses, prompt, conversation_history
            )

        # Крок 3: Синтезуємо фінальну відповідь з врахуванням follow-ups
        return await self._synthesize_consensus(
            responses, prompt, model, custom_prompt, conflicts, follow_up_data, conversation_history
        )

    def _detect_conflicts(self, responses: List[Dict[str, Any]]) -> List[Dict]:
        """Виявляємо конфлікти в відповідях"""
        conflicts = []
        
        for i, r1 in enumerate(responses):
            for j, r2 in enumerate(responses):
                if i >= j:
                    continue
                
                resp1 = r1.get("response", "").strip()
                resp2 = r2.get("response", "").strip()
                
                # Перевіряємо подібність текстів
                similarity = SequenceMatcher(None, resp1, resp2).ratio()
                
                # Якщо подібність менше 70% - це конфлікт
                if similarity < 0.7:
                    conflicts.append({
                        "model1": r1.get("model", "unknown"),
                        "model2": r2.get("model", "unknown"),
                        "response1": resp1,
                        "response2": resp2,
                        "similarity": similarity,
                    })
        
        return conflicts

    async def _request_follow_ups(
        self,
        conflicts: List[Dict],
        responses: List[Dict[str, Any]],
        original_prompt: str,
        conversation_history: List[Dict],
    ) -> Dict[str, str]:
        """Запрошуємо обґрунтування у конфліктних моделей"""
        follow_up_results = {}
        
        async with httpx.AsyncClient(timeout=300.0) as client:
            for conflict in conflicts:
                model1 = conflict["model1"]
                model2 = conflict["model2"]
                response1 = conflict["response1"]
                response2 = conflict["response2"]
                
                logger.info(f"[FOLLOW-UP] Запит до {model1} про конфлікт з {model2}")
                
                follow_up_prompt = FOLLOW_UP_REQUEST_TEMPLATE.format(
                    original_prompt=original_prompt,
                    your_response=response1,
                    conflicting_response=response2
                )
                
                try:
                    resp = await client.post(
                        f"{OLLAMA_HOST}/api/generate",
                        json={
                            "model": model1,
                            "prompt": follow_up_prompt,
                            "stream": False,
                            "options": {"temperature": 0.7, "top_p": 0.95}
                        }
                    )
                    resp.raise_for_status()
                    data = resp.json()
                    argumentation = data.get("response", "").strip()
                    
                    follow_up_results[model1] = argumentation
                    
                    logger.info(f"[FOLLOW-UP] {model1} відповів з обґрунтуванням ({len(argumentation)} символів)")
                    conversation_history.append({
                        "type": "follow_up",
                        "model": model1,
                        "question": "Обґрунтуйте вашу відповідь",
                        "argumentation": argumentation[:300]
                    })
                    
                except Exception as e:
                    logger.error(f"[FOLLOW-UP] Помилка при запиті до {model1}: {str(e)}")
                    follow_up_results[model1] = f"Помилка при запиті: {str(e)}"
        
        return follow_up_results

    async def _synthesize_responses(
        self,
        responses: List[Dict[str, Any]],
        prompt: str,
        model: str,
        custom_prompt: str | None,
        strategy: str,
        conversation_history: List[Dict],
    ) -> Dict[str, Any]:
        """Синтезуємо відповіді коли нема консенсусу"""
        user_prompt = custom_prompt or f"""Запит користувача:
{prompt}

Відповіді моделей:
{"\n\n".join([f"Модель {r['model']}: {r['response']}" for r in responses])}

Синтезуй найкращу відповідь на основі запиту та отриманих версій.
Об'єднай найсильніші частини, виправ помилки.

ФІНАЛЬНА ВІДПОВІДЬ: [синтезована відповідь]
ПОЯСНЕННЯ: [коротко - як синтезував]"""

        async with httpx.AsyncClient(timeout=300.0) as client:
            response = await client.post(
                f"{OLLAMA_HOST}/api/generate",
                json={
                    "model": model,
                    "prompt": user_prompt,
                    "system": ARBITER_SYSTEM_PROMPT,
                    "stream": False,
                    "options": {"temperature": 0.6, "top_p": 0.95}
                }
            )
            response.raise_for_status()
            data = response.json()

        full_text = data.get("response", "").strip()

        if "ПОЯСНЕННЯ:" in full_text:
            final, reasoning = full_text.split("ПОЯСНЕННЯ:", 1)
            final = final.replace("ФІНАЛЬНА ВІДПОВІДЬ:", "").strip()
            reasoning = reasoning.strip()
        else:
            final = full_text
            reasoning = "Синтезована відповідь на основі кількох моделей"

        logger.info(f"[{strategy.upper()}] Синтезована фінальна відповідь")
        conversation_history.append({
            "type": "synthesis",
            "strategy": strategy,
            "final_answer": final[:200]
        })

        return {
            "final_response": final,
            "reasoning": reasoning,
            "strategy": strategy,
            "arbiter_model": model,
            "confidence": 0.75,
            "conversation_history": conversation_history,
        }

    async def _synthesize_consensus(
        self,
        responses: List[Dict[str, Any]],
        prompt: str,
        model: str,
        custom_prompt: str | None,
        conflicts: List[Dict],
        follow_up_data: Dict[str, str],
        conversation_history: List[Dict],
    ) -> Dict[str, Any]:
        """Синтезуємо на основі консенсусу з follow-ups"""
        
        follow_up_section = ""
        if follow_up_data:
            follow_up_section = "\n\nОбґрунтування моделей при конфліктах:\n"
            for model, arg in follow_up_data.items():
                follow_up_section += f"\n{model}: {arg[:200]}..."

        user_prompt = custom_prompt or f"""Запит користувача:
{prompt}

Відповіді моделей:
{"\n\n".join([f"Модель {r['model']}: {r['response']}" for r in responses])}

{follow_up_section}

На основі цих відповідей і обґрунтувань виберіть найбільш логічну версію або синтезуйте найкращу.

ФІНАЛЬНА ВІДПОВІДЬ: [вибрана або синтезована]
ПОЯСНЕННЯ: [як був розв'язаний конфлікт]"""

        async with httpx.AsyncClient(timeout=300.0) as client:
            response = await client.post(
                f"{OLLAMA_HOST}/api/generate",
                json={
                    "model": model,
                    "prompt": user_prompt,
                    "system": STRATEGY_CONSENSUS_SYSTEM_PROMPT,
                    "stream": False,
                    "options": {"temperature": 0.6, "top_p": 0.95}
                }
            )
            response.raise_for_status()
            data = response.json()

        full_text = data.get("response", "").strip()

        if "ПОЯСНЕННЯ:" in full_text:
            final, reasoning = full_text.split("ПОЯСНЕННЯ:", 1)
            final = final.replace("ФІНАЛЬНА ВІДПОВІДЬ:", "").strip()
            reasoning = reasoning.strip()
        else:
            final = full_text
            reasoning = "Конфлікти розв'язані за консенсусом"

        logger.info(f"[CONSENSUS] Синтезована фінальна відповідь після follow-ups")
        conversation_history.append({
            "type": "consensus_synthesis",
            "conflicts_resolved": len(conflicts),
            "follow_ups_used": len(follow_up_data) > 0,
            "final_answer": final[:200]
        })

        return {
            "final_response": final,
            "reasoning": reasoning,
            "strategy": "consensus",
            "arbiter_model": model,
            "confidence": 0.85,
            "conversation_history": conversation_history,
            "consensus_info": {
                "conflicts_detected": len(conflicts),
                "follow_ups_conducted": len(follow_up_data) > 0,
                "follow_up_models": list(follow_up_data.keys()) if follow_up_data else [],
            }
        }
