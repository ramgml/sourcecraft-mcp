# SourceCraft MCP Server

MCP (Model Context Protocol) сервер для интеграции с платформой SourceCraft. Позволяет ИИ-агентам и IDE работать с репозиториями, issues, pull requests, CI/CD пайплайнами и релизами SourceCraft.

Пакет также включает CLI утилиту `sourcecraft` для работы с SourceCraft из терминала (см. [CLI утилита](#cli-утилита)).

## Установка

### Через pip

```bash
pip install sourcecraft-mcp
```

### Через uv (рекомендуется)

```bash
uv pip install sourcecraft-mcp
```

### Из исходников

```bash
git clone https://git.sourcecraft.dev/your-org/sourcecraft-mcp.git
cd sourcecraft-mcp
uv pip install -e .
```

### Установка без PyPI

#### 1. Установка из Git репозитория

Добавьте в `pyproject.toml` другого проекта:

```toml
[tool.uv.sources]
sourcecraft-mcp = { git = "https://git.sourcecraft.dev/your-org/sourcecraft-mcp.git" }
```

Или установите напрямую:

```bash
uv pip install "git+https://git.sourcecraft.dev/your-org/sourcecraft-mcp.git"
```

#### 2. Настройка MCP с использованием uv и git зависимостей

```json
{
  "mcpServers": {
    "sourcecraft": {
      "command": "uv",
      "args": [
        "run",
        "--with",
        "git+https://git.sourcecraft.dev/your-org/sourcecraft-mcp.git",
        "--with",
        "git+https://git.sourcecraft.dev/ram56/pysourcecraft.git@v0.1.0",
        "python",
        "-m",
        "sourcecraft_mcp.server"
      ],
      "env": {
        "SOURCECRAFT_API_TOKEN": "your-api-token"
      }
    }
  }
}
```

#### 3. Локальная разработка

Установите в режиме для разработки:

```bash
uv pip install -e /path/to/sourcecraft-mcp
```

Конфигурация MCP с PYTHONPATH:

```json
{
  "mcpServers": {
    "sourcecraft": {
      "command": "python",
      "args": ["-m", "sourcecraft_mcp.server"],
      "env": {
        "SOURCECRAFT_API_TOKEN": "your-api-token",
        "PYTHONPATH": "/path/to/sourcecraft-mcp/src"
      }
    }
  }
}
```

#### 4. Использование точки входа (после установки из git)

```json
{
  "mcpServers": {
    "sourcecraft": {
      "command": "sourcecraft-mcp",
      "env": {
        "SOURCECRAFT_API_TOKEN": "your-api-token"
      }
    }
  }
}
```

## Настройка

### Получение API токена

1. Войдите в [SourceCraft](https://sourcecraft.dev)
2. Перейдите в Settings → Access → Personal Access Tokens
3. Создайте новый токен с необходимыми правами

### Настройка окружения

Установите переменную окружения:

```bash
export SOURCECRAFT_API_TOKEN="your-api-token-here"
```

Или добавьте в `.env` файл:

```bash
SOURCECRAFT_API_TOKEN=your-api-token-here
SOURCECRAFT_BASE_URL=https://api.sourcecraft.tech  # опционально
```

### Настройка MCP клиента

Добавьте в конфигурацию MCP клиента (например, `.vscode/mcp.json` или `claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "sourcecraft": {
      "command": "uvx",
      "args": ["sourcecraft-mcp@latest"],
      "env": {
        "SOURCECRAFT_API_TOKEN": "your-api-token"
      }
    }
  }
}
```

Или для локальной разработки:

```json
{
  "mcpServers": {
    "sourcecraft": {
      "command": "python",
      "args": ["-m", "sourcecraft_mcp.server"],
      "env": {
        "SOURCECRAFT_API_TOKEN": "your-api-token"
      }
    }
  }
}
```

## Доступные инструменты

### Repositories (8 инструментов)

| Инструмент | Описание |
| ------------ | ---------- |
| `list_repositories` | Список репозиториев пользователя |
| `list_organization_repositories` | Список репозиториев организации |
| `get_repository` | Информация о репозитории |
| `create_repository` | Создать репозиторий |
| `update_repository` | Обновить репозиторий |
| `delete_repository` | Удалить репозиторий |
| `list_branches` | Список веток |
| `list_tags` | Список тегов |
| `get_file_tree` | Дерево файлов |

### Issues (10 инструментов)

| Инструмент | Описание |
|------------|----------|
| `list_issues` | Список issues с фильтрами |
| `get_issue` | Информация об issue |
| `create_issue` | Создать issue |
| `update_issue` | Обновить issue |
| `close_issue` | Закрыть issue |
| `reopen_issue` | Переоткрыть issue |
| `list_issue_comments` | Список комментариев |
| `add_issue_comment` | Добавить комментарий |

### Pull Requests (10 инструментов)

| Инструмент | Описание |
|------------|----------|
| `list_pull_requests` | Список PR с фильтрами |
| `get_pull_request` | Информация о PR |
| `create_pull_request` | Создать PR |
| `update_pull_request` | Обновить PR |
| `merge_pull_request` | Смержить PR |
| `publish_pull_request` | Опубликовать draft PR |
| `discard_pull_request` | Отклонить PR |
| `list_pr_reviewers` | Список ревьюеров |
| `add_pr_reviewer` | Добавить ревьюера |
| `set_review_decision` | Установить решение ревью |

### CI/CD (6 инструментов)

| Инструмент | Описание |
|------------|----------|
| `list_ci_runs` | Список CI запусков |
| `get_ci_run` | Информация о CI запуске |
| `get_workflow` | Информация о workflow |
| `get_cube_logs` | Логи CI cube |
| `get_artifacts` | Артефакты CI |
| `trigger_workflows` | Запустить workflows |

### Releases (7 инструментов)

| Инструмент | Описание |
|------------|----------|
| `list_releases` | Список релизов |
| `get_release` | Информация о релизе |
| `get_latest_release` | Последний релиз |
| `create_release` | Создать релиз |
| `update_release` | Обновить релиз |
| `publish_release` | Опубликовать релиз |
| `discard_release` | Отклонить релиз |

### Users & Organizations (7 инструментов)

| Инструмент | Описание |
|------------|----------|
| `get_current_user` | Текущий пользователь |
| `get_user` | Информация о пользователе |
| `list_my_issues` | Мои issues |
| `list_user_pull_requests` | PR пользователя |
| `list_organizations` | Список организаций |
| `get_organization` | Информация об организации |
| `list_organization_members` | Члены организации |

## Примеры использования

### Работа с репозиториями

```
> Покажи мне репозитории в организации myorg

Использую list_organization_repositories...

📦 frontend-app - Web application
📦 backend-api - API service
🔒 internal-tools - Internal utilities
```

### Работа с issues

```
> Найди все открытые issues с приоритетом critical в репозитории myorg/backend-api

Использую list_issues с фильтрами status=open и priority=critical...

🟢 #42 ⚠️ Database connection timeout
   Status: open | Priority: critical | Assignee: @dev1

🟢 #38 ⚠️ Memory leak in worker processes
   Status: open | Priority: critical | Assignee: @dev2
```

### Работа с Pull Requests

```
> Создай PR для ветки feature/new-auth в main в репозитории myorg/backend-api

Использую create_pull_request...

Pull request создан как draft!

#45: Implement new authentication flow
Branch: feature/new-auth → main
Author: @current-user
```

### Мониторинг CI/CD

```
> Покажи статус последних CI запусков в myorg/backend-api

Использую list_ci_runs...

CI/CD runs in 'myorg/backend-api':

✅ Run #abc123 - success
   Event: push
   Created: 2024-01-15 10:30 UTC

❌ Run #abc122 - failed
   Event: pull_request
   Created: 2024-01-15 09:45 UTC
```

## CLI утилита

Пакет включает CLI `sourcecraft` для работы с SourceCraft из терминала. Покрывает все домены API: репозитории, issues, pull requests, CI/CD, релизы, пользователи и организации.

### Аутентификация

```bash
export SOURCECRAFT_API_TOKEN="your-api-token"
# опционально
export SOURCECRAFT_BASE_URL="https://api.sourcecraft.tech"
```

Токен также можно передать флагом `--token`.

### Примеры команд

```bash
# Репозитории
sourcecraft repo list --org myorg
sourcecraft repo get myorg/backend-api
sourcecraft repo create my-service --visibility private
sourcecraft repo branches myorg/backend-api
sourcecraft repo tree myorg/backend-api --recursive

# Issues
sourcecraft issue list myorg/backend-api --status open
sourcecraft issue create myorg/backend-api --title "Bug" --body "Описание"
sourcecraft issue close myorg/backend-api 42

# Pull requests
sourcecraft pr list myorg/backend-api --status open
sourcecraft pr create myorg/backend-api --title "Fix" --source feature/x --target main --publish
sourcecraft pr merge myorg/backend-api 45 --squash
sourcecraft pr review myorg/backend-api 45 --decision approve

# CI/CD
sourcecraft ci runs myorg/backend-api
sourcecraft ci run myorg/backend-api <run-slug>
sourcecraft ci logs myorg/backend-api <run> <workflow> <task> <cube>
sourcecraft ci trigger myorg/backend-api build --branch main

# Релизы
sourcecraft release list myorg/backend-api
sourcecraft release create myorg/backend-api v1.0.0 --title "First release" --publish

# Пользователи и организации
sourcecraft user me
sourcecraft user prs username --role reviewer
sourcecraft org list
sourcecraft org members myorg
```

### Формат вывода

По умолчанию вывод — читаемые таблицы (Rich). Глобальный флаг `--json` переключает вывод в JSON для скриптов:

```bash
sourcecraft --json repo list --org myorg | jq '.repositories[].slug'
```

## Разработка

### Установка зависимостей

```bash
uv sync
```

### Запуск тестов

```bash
uv run pytest
```

### Линтинг

```bash
uv run ruff check .
uv run ruff format .
```

### Структура проекта

```
src/sourcecraft_mcp/
├── __init__.py
├── server.py          # Точка входа MCP сервера
├── cli/               # CLI утилита (команда `sourcecraft`)
│   ├── app.py         # Точка входа CLI, глобальные опции
│   ├── common.py      # Общие хелперы (клиент, вывод, ошибки)
│   ├── repos.py
│   ├── issues.py
│   ├── prs.py
│   ├── cicd.py
│   ├── releases.py
│   ├── users.py
│   └── orgs.py
├── tools/             # Инструменты по доменам
│   ├── repositories.py
│   ├── issues.py
│   ├── pull_requests.py
│   ├── cicd.py
│   ├── releases.py
│   ├── users.py
│   └── organizations.py
└── utils.py           # Утилиты
```

## Лицензия

MIT License
