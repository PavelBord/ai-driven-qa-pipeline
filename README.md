# AI-Driven QA Pipeline

## Описание проекта

AI-Driven QA Pipeline — это автоматизированный пайплайн для генерации QA-артефактов с использованием LLM.

Цель проекта — автоматизировать процесс подготовки тестовой документации и автотестов:

- анализ бизнес-требований;
- защита данных (PII masking);
- генерация тестовых сценариев;
- генерация pytest автотестов;
- AI code review;
- автоматическая валидация результатов.

Проект использует локальную LLM через Ollama.

---

# Архитектура проекта

Business Requirements
          |
          v
+----------------+
|   PII Stage     |
| Data Masking    |
+----------------+
          |
          v
+----------------+
| Scenario       |
| Generator     |
| LLM           |
+----------------+
          |
          v
+----------------+
| Test Contract |
| Validation    |
+----------------+
          |
          v
+----------------+
| Code Generator|
| Pytest        |
+----------------+
          |
          v
+----------------+
| Code Reviewer |
| LLM Review    |
+----------------+
          |
          v
Generated Tests

---

# Основные возможности

## 1. PII Protection

Перед передачей данных в LLM выполняется поиск и маскирование персональных данных.

Пример:

До:

```yaml
email: user@test.com
password: password123
После:
email: <EMAIL>
password: <PASSWORD>
Создаются артефакты:
artifacts/pii/
├── pii-report.json
└── masked-business-checklist.yaml
2. Генерация тестовых сценариев
AI анализирует бизнес-требования и создает тестовый контракт.
Пример:
{
  "test_cases": [
    {
      "id": "TC-001",
      "requirement_id": "AUTH-001",
      "title": "Successful authentication",
      "type": "positive",
      "priority": "high"
    }
  ]
}
Все сценарии проходят JSON Schema validation.
Проверяется:
- наличие обязательных полей;
- корректность requirement_id;
- покрытие всех требований;
- отсутствие лишних данных.
3. Генерация pytest кода
Для каждого тест-кейса создается отдельный pytest файл.
Пример:
artifacts/generated/

test_TC_001.py
test_TC_002.py
test_TC_003.py
test_TC_004.py
test_TC_005.py
Пример сгенерированного теста:
def test_TC_001():

    email = "<EMAIL>"
    password = "<PASSWORD>"

    pass
На данном этапе создается тестовый каркас.
4. AI Code Review
После генерации pytest кода выполняется автоматический review через LLM.
Проверяется:
- наличие pytest функции;
- корректность структуры;
- потенциальные проблемы;
- рекомендации по улучшению.
Ответ AI:
{
  "status": "passed",
  "issues": [],
  "recommendations": []
}
Используемые технологии
Backend
- Python 3.12
- uv
- pytest
- jsonschema
- PyYAML
AI
- Ollama
- Gemma LLM
Quality Tools
- ruff
- mypy
Структура проекта
ai-driven-qa-pipeline/

├── input/
│   └── business-checklist.yaml

├── prompts/
│   ├── test-scenario-generation.txt
│   ├── test-code-generation.txt
│   └── code-review.txt

├── src/
│   └── pipeline/
│       ├── pii/
│       ├── scenario/
│       ├── codegen/
│       ├── code_reviewer/
│       └── llm/

├── artifacts/

│   ├── pii/
│   ├── scenarios/
│   └── generated/

├── tests/

├── pyproject.toml

└── README.md