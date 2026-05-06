# JSON Result Schema for LLM Ensemble

```json
{
  "schema_version": "string",
  "request_id": "string",
  "original_query": "string",
  "timestamp": "string",

  "workers": [
    {
      "worker_id": "string",
      "model": "string",
      "answer": "string",
      "confidence": "float"
    }
  ],

  "arbiter": {
    "final_answer": "string",
    "strategy": "string",
    "confidence": "float",
    "reasoning": "string",
    "selected_from": ["string"],
    "rejection_reasons": {
      "worker_id": "string"
    },
    "confidence_distribution": {
      "worker_id": "float"
    }
  },

  "evaluation": {
    "correct": "boolean",
    "agreement_score": "float",
    "disagreement_score": "float",
    "consensus": "boolean",
    "model_errors": {
      "worker_id": "boolean"
    }
  },

  "ground_truth": "string | null",

  "metrics": {
    "latency_ms": "integer",
    "tokens_total": "integer"
  },

  "notes": "string | null"
}
```

# JSON SCHEMA Пояснення

# Top-level fields

### schema_version [string]
Версія цієї схеми результату (для майбутньої сумісності).

### request_id [string]
Унікальний ідентифікатор запиту.

### original_query [string]
Оригінальний запит користувача.

### timestamp [string]
Час створення результату (рекомендовано ISO 8601).

# workers [array]
Масив відповідей від усіх worker-моделей.

### worker_id [string]
Унікальний ідентифікатор worker-а (має бути унікальним).

### model [string]
Назва моделі (наприклад: `qwen2.5-32b-instruct`).

### answer [string]
Повна відповідь, згенерована моделлю.

### confidence [float]
Впевненість моделі у відповіді (0.0 — 1.0).

# arbiter [object]
Результат роботи Арбітра.

### final_answer [string]
Фінальна відповідь, яку бачить користувач.

### strategy [string]
Стратегія арбітра (majority, best-confidence, synthesis тощо).

### confidence [float]
Загальна впевненість арбітра.

### reasoning [string]
Пояснення арбітра, чому саме така фінальна відповідь.

### selected_from [array]
Список worker_id, які були використані для фінальної відповіді.

### rejection_reasons [object]
Причини відхилення worker-ів (ключ = worker_id).

### confidence_distribution [object]
Розподіл впевненості (ключ = worker_id).

# evaluation [object]
Оцінка якості (для evaluation mode).

### correct [boolean]
Чи співпадає з ground_truth.

### agreement_score [float]
Рівень згоди між worker-моделями.

### disagreement_score [float]
Рівень розбіжності між worker-моделями.

### consensus [boolean]
Чи досягнуто консенсусу.

### model_errors [object]
Позначки помилок (ключ = worker_id).

## ground_truth [string | null]
Еталонна відповідь (null якщо немає).

# metrics [object]
Технічні метрики виконання.

### latency_ms [integer]
Загальний час виконання.

### tokens_total [integer]
Загальна кількість токенів.

## notes [string | null]
Додаткові нотатки.
