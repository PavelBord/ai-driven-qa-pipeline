# 🤖 AI-Driven QA Pipeline

## 📌 Overview

AI-Driven QA Pipeline — автоматизированный pipeline для генерации и проверки pytest автотестов на основе бизнес-требований.

Проект демонстрирует использование LLM в процессе QA Automation:

- анализ требований;
- защита тестовых данных от утечки PII;
- генерация тестовых сценариев;
- создание test contract;
- генерация pytest-кода;
- AI code review;
- автоматическая проверка качества кода.

Основная идея проекта:

> Превратить бизнес-требование в готовый проверенный автотест с помощью AI.

---

# 🏗 Architecture

Pipeline состоит из следующих этапов:

```
Business Requirements
        |
        v
+----------------+
|  PII Detection |
|  & Masking     |
+----------------+
        |
        v
+----------------+
| AI Scenario    |
| Generator      |
+----------------+
        |
        v
+----------------+
| Test Contract  |
| Validation     |
+----------------+
        |
        v
+----------------+
| Pytest Code    |
| Generation     |
+----------------+
        |
        v
+----------------+
| AI Code Review |
+----------------+
        |
        v
Generated Tests
```

---

# 🚀 Features

## 🔐 PII Protection

Перед передачей данных в AI pipeline выполняется проверка персональных данных.

Поддерживается:

- email detection;
- password detection;
- masking sensitive information.

Пример:

До:

```yaml
email: user@example.com
password: secret123
```

После:

```yaml
email: <EMAIL>
password: <PASSWORD>
```

---

## 🧠 AI Scenario Generation

LLM анализирует бизнес-требования и создает тестовые сценарии.

Генерируется:

- test case ID;
- requirement ID;
- title;
- description;
- priority;
- test steps;
- expected result.

Пример:

```json
{
  "id": "TC-001",
  "requirement_id": "AUTH-001",
  "title": "Successful authentication",
  "type": "positive"
}
```

---

## 📋 Test Contract Validation

Перед генерацией кода выполняется проверка контракта.

Проверяется:

- обязательные поля;
- корректность requirement_id;
- наличие test steps;
- покрытие всех требований.

Если контракт невалидный:

```
ContractValidationError
```

останавливает pipeline.

---

## 🧪 Pytest Code Generation

AI генерирует pytest тесты только на основании test contract.

Пример результата:

```python
def test_TC_001():
    email = "<EMAIL>"
    password = "<PASSWORD>"

    pass
```

Pipeline запрещает AI придумывать:

- URL;
- API endpoints;
- HTTP методы;
- UI элементы;
- локаторы.

---

## 🔍 AI Code Review

После генерации тестов выполняется AI review.

Проверяется:

- наличие pytest функции;
- качество кода;
- потенциальные проблемы;
- рекомендации.

Ответ сохраняется в JSON формате:

```json
{
  "status": "passed",
  "issues": [],
  "recommendations": []
}
```

---

# 🛠 Tech Stack

## Programming

- Python 3.12

## Testing

- pytest

## AI

- Ollama
- Gemma / LLM models

## Quality Tools

- mypy
- ruff

## Environment

- uv

---

# 📂 Project Structure

```
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
│       └── contract_validator.py

├── artifacts/

│   ├── pii/
│   ├── scenarios/
│   └── generated/

├── tests/

├── pyproject.toml

└── README.md
```

---

# ▶️ Installation

Clone repository:

```bash
git clone https://github.com/PavelBord/ai-driven-qa-pipeline.git
```

Go to project:

```bash
cd ai-driven-qa-pipeline
```

Install dependencies:

```bash
uv sync
```

---

# ▶️ Run Pipeline

Запуск полного pipeline:

```bash
uv run python -m pipeline.full_pipeline
```

После выполнения создаются:

```
artifacts/

├── pii/
│   ├── pii-report.json
│   └── masked-business-checklist.yaml

├── scenarios/
│   └── test-scenarios.json

└── generated/
    ├── test_TC_001.py
    ├── test_TC_002.py
    └── ...
```

---

# ✅ Quality Gates

## Pytest

Запуск:

```bash
uv run pytest artifacts/generated
```

Результат:

```
5 passed
```

---

## Mypy

Проверка типов:

```bash
uv run mypy src
```

Результат:

```
Success: no issues found
```

---

## Ruff

Проверка качества:

```bash
uv run ruff check src
```

Результат:

```
All checks passed!
```

---

# 🎯 Project Goal

Цель проекта — показать применение AI в QA Automation:

- уменьшение времени создания тестов;
- повышение качества тестовых сценариев;
- автоматизация повторяющихся QA процессов;
- использование LLM как помощника инженера.

---

# 👨‍💻 Author

Pavel Bordukov

QA Automation Engineer

GitHub:

https://github.com/PavelBord