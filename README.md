# 🚀 OpenAPI Client Generator

Универсальный генератор Python-клиентов из OpenAPI спецификаций.

## ✨ Возможности

- 🎯 **Универсальная команда** с поддержкой конфигурационных файлов
- 🏗️ **Модульная архитектура** - чистая internal структура
- 🔧 **Интерактивная настройка** - выбор между конфигом и аргументами
- ⚡ **Чистые endpoints** - генерация через `locals()` без лишних переменных
- 🎨 **Консистентные имена** - единообразие между endpoints и моделями
- 📦 **Production-ready** - aiohttp клиент с connection pooling
- 🔒 **Type-safe** - полная типизация с Pydantic моделями

## 📥 Установка

```bash
pip install api-to-client
```

## 🚀 Использование

### Быстрый старт

```bash
# Генерация клиента напрямую
openapi-client --url http://localhost:8000 --dirname my_api

# Создание конфигурационного файла
openapi-client --init-config --url http://localhost:8000 --dirname my_api

# Генерация из конфига
openapi-client
```

### Конфигурационный файл

Создайте файл `openapi.toml`:

```toml
# URL к OpenAPI спецификации
url = "http://localhost:8000"

# Папка для генерации клиента
dirname = "my_api"

# Исправлять некорректные имена
fix_names = true
```

### Интерактивное разрешение конфликтов

Если есть и конфиг и аргументы командной строки, генератор спросит что использовать:

```bash
$ openapi-client --dirname other_api

🔧 Найден конфиг файл openapi.toml:
   URL: http://localhost:8000
   Директория: my_api
   Исправлять имена: True

📝 Переданы аргументы:
   Директория: other_api

Использовать конфиг из файла? (y/n):
```

## 📁 Структура сгенерированного клиента

```
my_api/
├── __init__.py              # ApiClient, EndPoints, models
├── client.py                # Основной ApiClient класс
├── common.py                # Production aiohttp клиент
├── py.typed                 # Type hints marker
├── lib/
│   ├── __init__.py
│   ├── models.py            # NOTSET, MethodName
│   └── exc.py               # Типизированные исключения
├── endpoints/               # Модульные endpoints по тегам
│   ├── __init__.py          # EndPoints агрегатор
│   ├── authentication.py    # Методы аутентификации
│   ├── users.py             # Пользовательские методы
│   └── ...
└── models/                  # Pydantic модели по тегам
    ├── __init__.py          # Re-export всех моделей
    ├── authentication.py    # LoginResponse, UserShort
    ├── users.py             # UserRead, UserCreate
    └── ...
```

## 💻 Использование сгенерированного клиента

### Базовое использование

```python
from my_api import ApiClient

# Инициализация
client = ApiClient()

# Два способа вызова методов:

# 1. Через endpoints (структурированный доступ)
await client.endpoints.authentication.login(
    username_body="admin",
    password_body="secret"
)

# 2. Прямой доступ (удобный способ)
await client.login(
    username_body="admin", 
    password_body="secret"
)
```

### Параметры с суффиксами

Все параметры имеют понятные суффиксы:

```python
# Path параметры
await client.get_user(user_id_path=123)

# Query параметры  
await client.get_users(limit_query=10, offset_query=0)

# Body параметры
await client.create_user(name_body="John", email_body="john@example.com")

# File параметры
await client.upload_avatar(avatar_file=file_data)
```

### Типизация

```python
from my_api import ApiClient
from my_api.models.users import UserRead, UserCreate

client = ApiClient()

# Полная типизация в IDE
user_data = UserCreate(name="John", email="john@example.com")
user: UserRead = await client.create_user(name_body=user_data.name, email_body=user_data.email)
```

## 🔧 Параметры команды

```
openapi-client [OPTIONS]

Опции:
  --url TEXT        URL к OpenAPI спецификации
  --dirname TEXT    Директория для генерации клиента
  --fix             Исправлять некорректные имена
  --init-config     Создать конфигурационный файл openapi.toml
  --help           Показать справку
```

## 🏗️ Архитектура

### Internal структура

```
api_to_client/
├── internal/                # 🔒 Внутренняя реализация
│   ├── generator/           # Генераторы кода
│   │   ├── client_generator.py
│   │   ├── templates.py
│   │   └── http_client.py
│   ├── parser/              # Парсинг OpenAPI
│   │   └── openapi.py
│   └── types/               # Модели данных
│       ├── models.py
│       └── schema_resolver.py
├── generator.py             # 🌟 Чистый публичный API
├── config.py                # Конфигурация
└── cli.py                   # CLI интерфейс
```

### Чистые endpoints

Генерируемые методы используют современный подход с `locals()`:

```python
async def login(self, username_body: str, password_body: str):
    path = '/auth/login'
    data = {k.replace('_body', ''): v 
            for k, v in locals().items() 
            if k.endswith('_body') and not models.is_not_set(v)}
    response = await self.client._send_request(
        method='post', path=path, data=json.dumps(data)
    )
    return response.json() if response.status_code < 300 else response.content
```

## 🎯 Особенности

- **Универсальность**: Работает с любыми OpenAPI спецификациями
- **Модульность**: Endpoints и модели разделены по тегам
- **Консистентность**: Имена схем совпадают в endpoints ↔ models
- **Производительность**: Production-ready aiohttp с connection pooling
- **Удобство**: Два способа доступа к методам + автодополнение в IDE
- **Чистота**: Минимальный код без дублирования

## 📖 Примеры

### Создание конфига и генерация

```bash
# Создаем конфиг
openapi-client --init-config --url http://api.example.com --dirname my_client

# Редактируем openapi.toml если нужно

# Генерируем клиент
openapi-client
```

### Работа с файлами

```python
# Upload файла
with open('document.pdf', 'rb') as f:
    result = await client.upload_document(file_file=f)

# Множественная загрузка
files = [
    ('documents', open('doc1.pdf', 'rb')),
    ('documents', open('doc2.pdf', 'rb'))
]
await client.upload_multiple(files_file=files)
```

### Обработка ошибок

```python
from my_api.lib.exc import ValidationError, AuthenticationError

try:
    user = await client.get_user(user_id_path=999)
except ValidationError as e:
    print(f"Ошибка валидации: {e.message}")
except AuthenticationError:
    print("Требуется аутентификация")
```

## 🔄 Миграция с предыдущих версий

Старые команды `gen-api` и `update-api` помечены как deprecated. 
Используйте новую универсальную команду `openapi-client`.

## 🏆 Результат

Генератор создает **enterprise-grade** Python пакеты с:

- ✅ Чистой архитектурой
- ✅ Полной типизацией  
- ✅ Production-ready HTTP клиентом
- ✅ Модульной структурой
- ✅ Интуитивным API

---

**Превратите любую OpenAPI спецификацию в профессиональный Python клиент!** 🚀