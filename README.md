# AI-Driven QA Pipeline

Генерация и исполнение Playwright-тестов на основе исходных требований и описания страниц с помощью локальной LLM (Ollama). Пайплайн закрывает весь цикл: от бизнес-чеклиста до готовых тестов, code review, баг-репортов и отчета о выполнении.

## Возможности

- Генерация Playwright-тестов из бизнес-чеклиста (YAML) с помощью LLM
- Автоматическое создание page objects по описанию страниц
- Маскирование PII-данных до отправки в LLM
- Автоматический code review сгенерированного кода
- Генерация баг-репортов по результатам code review и выполнения тестов
- Запуск сгенерированных тестов и формирование сводки
- Mock LLM client для CI и оффлайн-проверок (без запуска Ollama)
- Статические проверки: `ruff`, `mypy` (для сгенерированного кода — также `black`)

## Требования

- Python 3.12 (`>=3.12,<3.13`)
- `uv` (менеджер зависимостей)
- Ollama с моделью LLM (по умолчанию `gemma4:12b`) для локальной генерации
- Браузеры Playwright (для исполнения тестов)

## Быстрый старт

```bash
# 1. Установка зависимостей
uv sync

# 2. Установка браузеров Playwright (для исполнения)
uv run playwright install chromium

# 3. Запуск полного пайплайна (требует запущенного Ollama)
uv run python -m pipeline.full_pipeline

# 4. Для CI / оффлайн — запуск с mock LLM (без Ollama)
CI=true uv run python -m pipeline.full_pipeline
```

## Структура проекта

```
ai-driven-qa-pipeline/
├── input/                         # Исходные бизнес-чеклисты
│   └── demo-web-shop-checklist.yaml
├── prompts/                       # Шаблоны промптов для LLM
├── schemas/                       # JSON-схемы контрактов
├── src/
│   ├── page_objects/              # Готовые page objects (пример)
│   └── pipeline/
│       ├── bug_report/            # Генератор баг-репортов
│       ├── code_reviewer/         # Code review сгенерированного кода
│       ├── codegen/               # Генерация и валидация кода
│       ├── execution/             # Запуск тестов
│       ├── llm/                   # LLM клиенты (Ollama, Mock)
│       ├── page_objects/          # Генерация page objects
│       ├── pii/                   # Маскирование PII
│       ├── scenario/              # Генерация сценариев
│       ├── config.py              # Пути к директориям
│       ├── contract_validator.py  # Проверка контракта
│       ├── reporting.py           # Манифест и отчеты
│       └── full_pipeline.py       # Точка входа пайплайна
├── tests/
│   ├── unit/                      # Юнит-тесты (49 тестов)
│   └── e2e/                       # Playwright e2e на demo-shop
├── artifacts/                     # Результаты (в .gitignore)
├── .github/workflows/qa-pipeline.yml  # CI
├── .pre-commit-config.yaml
├── pyproject.toml
└── uv.lock
```

## Как это работает

Бизнес-чеклист (`input/*.yaml`) содержит:

- `application` — имя и URL приложения
- `pages` — описания страниц и элементов (locator, type)
- `requirements` — пользовательские требования (USER-001, PRODUCT-001 и т.д.)

Пайплайн выполняет следующие шаги:

1. **PII-стадия** — маскирует чувствительные значения (пароли, токены, email) перед отправкой в LLM
2. **Генерация page objects** — создаёт код страниц из раздела `pages`
3. **Генерация сценариев** — строит тест-контракт с тест-кейсами по требованиям
4. **Генерация кода тестов** — LLM пишет Playwright-тесты по контракту и page objects
5. **Code review** — проверка сгенерированного кода, при неудаче — баг-репорт
6. **Валидация кода** — AST-проверки: одна `test_*` функция, запрет прямых `page.click/fill/goto`, запрет хардкод-локаторов
7. **Исполнение** — запуск сгенерированных тестов, сводка и баг-репорты по падениям
8. **Манифест** — `artifacts/manifest.json` со всеми созданными артефактами

## Результаты

Все артефакты попадают в `artifacts/`:

```
artifacts/
├── pii/            # Маскированный чеклист
├── pages/          # Сгенерированные page objects
├── scenarios/      # test-scenarios.json (тест-контракт)
├── generated/      # Сгенерированные Playwright-тесты
├── code-review/    # Результаты ревью
├── bug-reports/    # Баг-репорты
├── execution/      # Сводка выполнения тестов
└── manifest.json
```

## Тестирование проекта

```bash
# Юнит-тесты
uv run pytest

# Юнит + e2e
uv run pytest tests/unit tests/e2e

# Статические проверки
uv run ruff check src tests
uv run mypy src

```

## CI/CD

GitHub Actions workflow `.github/workflows/qa-pipeline.yml`:

- генерация тестов с mock LLM (`CI=true`)
- исполнение сгенерированных тестов
- качество сгенерированного кода (`black --check`, `ruff`)
- линт + type check исходников
- загрузка артефактов

## Лицензия

MIT — см. файл [LICENSE](LICENSE).