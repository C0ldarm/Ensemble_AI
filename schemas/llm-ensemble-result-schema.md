# JSON Result Schema for LLM Ensemble

```json
{
  "question_id": "string",
  "timestamp": "string (ISO 8601)",

  "workers": [
    {
      "worker_id": "string",
      "model": "string",
      "answer": "string",
      "confidence": "float (0.0 - 1.0)"
    }
  ],

  "arbiter": {
    "final_answer": "string",
    "strategy": "string",
    "confidence": "float (0.0 - 1.0)",
    "reasoning": "string"
  },

  "evaluation": {
    "correct": "boolean",
    "agreement_score": "float (0.0 - 1.0)",
    "disagreement_score": "float (0.0 - 1.0)",
    "consensus": "boolean",

    "model_errors": {
      "worker_1": "boolean",
      "worker_2": "boolean",
      "worker_3": "boolean"
    }
  },

  "ground_truth": "string",
  "metrics": {
    "latency_ms": "integer",
    "tokens_total": "integer",
    "cost_estimate": "float"
  },

  "notes": "string"
}
```

# JSON SCHEMA Пояснення

## question_id [string]
Унікальний ідентифікатор запитання в системі.  
Використовується для трекінгу експериментів і порівняння результатів.

## timestamp [string (ISO 8601)]
Час запуску експерименту у форматі ISO 8601.  
Наприклад: 2026-05-06T21:30:00Z

## workers [array]

Список всіх моделей, які брали участь у відповіді.

### worker_id [string]
Унікальний ідентифікатор конкретного інстансу моделі.  
Дозволяє розрізняти однакові моделі, запущені паралельно.

### model [string]
Назва або тип моделі.

Приклади:
- qwen2.5-7b  
- llama3-8b  
- mistral-7b  

### answer [string]
Відповідь, яку згенерувала модель.

### confidence [float (0.0 – 1.0)]
Впевненість моделі у відповіді (0.0 – 1.0)

## arbiter [object]

Компонент, який агрегує відповіді workers.

### final_answer [string]
Фінальна відповідь системи після агрегації.

### strategy [string]
Метод прийняття рішення:

- majority — більшість  
- consensus — повна згода  
- conflict — конфлікт  
- weighted — зважене рішення  

### confidence [float (0.0 – 1.0)]
Впевненість арбітра у фінальній відповіді.

### reasoning [string]
Пояснення вибору відповіді.

## evaluation [object]

Метрики якості системи.

### correct [boolean]
Чи правильна фінальна відповідь (якщо є ground truth).

### agreement_score [float (0.0 – 1.0)]
Рівень згоди між моделями.

1.0 = повна згода  
0.0 = повна розбіжність  

### disagreement_score [float (0.0 – 1.0)]
Рівень розбіжності між моделями.

### consensus [boolean]
Чи є домінуюча спільна відповідь.

### model_errors [object]

Позначення помилок моделей.

Приклад:
worker_1: true  
worker_2: false  

true = помилка  
false = правильно

## ground_truth [string]
Правильна відповідь (для оцінки системи).

## metrics [object]

Технічні метрики виконання.

### latency_ms [integer]
Час виконання запиту.

### tokens_total [integer]
Загальна кількість токенів.

### cost_estimate [float]
Оцінка ресурсів (опціонально).

## notes [string]
Додаткові спостереження або коментарі.