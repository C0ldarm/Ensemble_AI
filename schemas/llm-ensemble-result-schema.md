# JSON Result Schema for LLM Ensemble

[{
  "question_id": null,
  "timestamp": null,

  "workers": [
    {
      "worker_id": null,
      "model": null,
      "answer": null,
      "confidence": null
    }
  ],

  "arbiter": {
    "final_answer": null,
    "strategy": null,
    "confidence": null,
    "reasoning": null
  },

  "evaluation": {
    "correct": null,
    "agreement_score": null,
    "disagreement_score": null,
    "consensus": null,

    "model_errors": {
      "worker_1": null,
      "worker_2": null,
      "worker_3": null
    }
  },

  "ground_truth": null,

  "metrics": {
    "latency_ms": null,
    "tokens_total": null,
    "cost_estimate": null
  },

  "notes": null
}]

# JSON SCHEMA Пояснення

## question_id [string | null]
Унікальний ідентифікатор запитання в системі.  
Використовується для трекінгу експериментів і порівняння результатів.

## timestamp [string | null]
Час запуску експерименту у форматі ISO 8601.  
Наприклад: 2026-05-06T21:30:00Z

## workers [array]

Список всіх моделей, які брали участь у відповіді.

### worker_id [string | null]
Унікальний ідентифікатор конкретного інстансу моделі.  
Дозволяє розрізняти однакові моделі, запущені паралельно.

### model [string | null]
Назва або тип моделі.

Приклади:
- qwen2.5-7b  
- llama3-8b  
- mistral-7b  

### answer [string | null]
Відповідь, яку згенерувала модель.

### confidence [float | null]
Впевненість моделі у відповіді (0.0 – 1.0)

## arbiter [object]

Компонент, який агрегує відповіді workers.

### final_answer [string | null]
Фінальна відповідь системи після агрегації.

### strategy [string | null]
Метод прийняття рішення:

- majority — більшість  
- consensus — повна згода  
- conflict — конфлікт  
- weighted — зважене рішення  

### confidence [float | null]
Впевненість арбітра у фінальній відповіді.

### reasoning [string | null]
Пояснення вибору відповіді.

## evaluation [object]

Метрики якості системи.

### correct [boolean | null]
Чи правильна фінальна відповідь (якщо є ground truth).

### agreement_score [float | null]
Рівень згоди між моделями.

1.0 = повна згода  
0.0 = повна розбіжність  

### disagreement_score [float | null]
Рівень розбіжності між моделями.

### consensus [boolean | null]
Чи є домінуюча спільна відповідь.

### model_errors [object]

Позначення помилок моделей.

Приклад:
worker_1: true  
worker_2: false  

true = помилка  
false = правильно

## ground_truth [string | null]
Правильна відповідь (для оцінки системи).

## metrics [object]

Технічні метрики виконання.

### latency_ms [number | null]
Час виконання запиту.

### tokens_total [number | null]
Загальна кількість токенів.

### cost_estimate [number | null]
Оцінка ресурсів (опціонально).

## notes [string | null]
Додаткові спостереження або коментарі.
