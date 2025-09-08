# FastAPI Client Generator

Мощный генератор Python клиентов из OpenAPI спецификаций с современной архитектурой и FastAPI-style декораторами.

## 🚀 Особенности

### 📁 **Умная генерация моделей**
- **Отдельная схема в каждом файле** (`users_create.py` → `UsersCreate`)
- **Интеллектуальные имена**: `UsersCreate` вместо `SchemasCreate`
- **TYPE_CHECKING imports** для forward references
- **Автоматический model_rebuild()** для правильной работы Pydantic

### 🎨 **FastAPI-style декораторы**
- **Чистые endpoint'ы** с декораторами `@get`, `@post`, `@put`, `@delete`, `@patch`
- **Автоматическая обработка** path/query/body параметров
- **Полная типизация** с IDE поддержкой

### 🏗️ **Современная архитектура**
- **Упрощенная структура** без лишних папок
- **Контекстное управление** headers и cookies
- **Универсальная обработка** content-types (JSON, XML, binary)
- **Автогенерация ссылок** на связанные модели

## 📦 Установка

```bash
pip install git+https://github.com/PythonPackageArea/OpenApiClient.git
```

## 🔧 Использование

### Command Line

```bash
# Генерация из URL
openapi_client --url https://petstore.swagger.io/v2/swagger.json --dirname petstore_client
openapi_client --url https://0.0.0.0:8000 --dirname petstore_client # Самостоятельно пропишет /openapi.json

# Генерация из файла
openapi_client --url ./openapi.json --dirname my_client

# Режим интерактивного меню
openapi_client
```

### Программное использование

```python
from openapi_client.generator import ApiClientGenerator

# Из URL
generator = ApiClientGenerator.from_url("https://api.example.com/openapi.json")
project = generator.generate()
project.save("./my_client")

# Из файла
generator = ApiClientGenerator.from_file("./openapi.json")
project = generator.generate()
project.save("./my_client")
```

## 🏗️ Структура сгенерированного клиента

```
📦 my_client/
├── 📄 constants.py        # NOTSET константа
├── 📄 utils.py            # is_not_set + обработка запросов
├── 📄 decorators.py       # FastAPI-style декораторы
├── 📄 common.py           # HTTP клиент + исключения
├── 📄 client.py           # Главный API клиент
├── 📁 models/             # Pydantic модели
│   ├── 📄 __init__.py     # Централизованный экспорт + model_rebuild()
│   ├── 📄 users_create.py # UsersCreate
│   ├── 📄 users_read.py   # UsersRead
│   └── 📄 ...
└── 📁 endpoints/          # Endpoint классы
    ├── 📄 users.py        # class Users + ссылки на модели
    ├── 📄 auth.py         # class Auth + ссылки на модели
    └── 📄 ...
```

## 💡 Примеры использования

### Базовое использование

```python
from my_client import ApiClient

# Инициализация
client = ApiClient()
client.initialize("https://api.example.com")

# Аутентификация
auth_response = await client.auth.login(
    username_body="user123", 
    password_body="secret"
)

# Установка Bearer токена
client.set_auth_token(auth_response.token)

# API запросы с автоматическим парсингом
users = await client.users.find_many(limit_query=10)
print(f"Найдено пользователей: {len(users.data)}")

# Создание нового пользователя  
new_user = await client.users.create(
    name_body="John Doe",
    email_body="john@example.com"
)
```

### Контекстное управление headers

```python
# Постоянные заголовки
client.update_headers(ApiVersion="v2", UserAgent="MyApp/1.0")

# Временные заголовки (только для блока)
async with client.with_headers(Debug="true", Trace="enabled"):
    debug_data = await client.users.get_debug_info()
# Debug заголовки автоматически убираются

# Временные cookies
async with client.with_cookies(session_id="abc123", locale="ru"):
    localized_data = await client.content.get_localized()
```

### Работа с моделями

```python
# Прямой доступ к моделям через endpoint класс
UserModel = client.users.users_read
CreateModel = client.users.users_create
PaginatedModel = client.users.users_paginated

# Создание экземпляров
new_user_data = CreateModel(
    name="Jane Doe", 
    email="jane@example.com"
)

# Type hints в функциях
def process_users(paginated: client.users.users_paginated):
    for user in paginated.data:
        print(f"User: {user.name}")

# Валидация данных
try:
    user = UserModel(**user_data)
except ValidationError as e:
    print(f"Ошибка валидации: {e}")
```

### Обработка разных content-types

```python
# JSON API (автоматический парсинг в Pydantic)
users = await client.users.find_many()  # → UsersPaginated

# CSV export
csv_data = await client.reports.export_csv()  # → str

# PDF generation  
pdf_bytes = await client.reports.generate_pdf()  # → bytes

# XML API
xml_data = await client.legacy.get_xml_data()  # → str

# Health check (plain text)
status = await client.health.status()  # → str "OK"
```

## 🎨 Особенности генерации

### Умные имена схем

```python
# ❌ Старый подход
schemas.Create → SchemasCreate  # Неинформативно
schemas.Read → SchemasRead      # Непонятно что это

# ✅ Новый подход  
apps__users__schemas__Users__Create → UsersCreate    # Понятно!
apps__posts__schemas__Posts__Read → PostsRead        # Информативно!
```

### FastAPI-style декораторы

```python
# Сгенерированный endpoint класс
class Users:
    # Автоматические ссылки на связанные модели
    users_create = UsersCreate
    users_read = UsersRead  
    users_paginated = UsersPaginated
    user_profile = UserProfile

    @post('/users', response_model=UsersRead)
    async def create(
        self,
        name_body: str = NOTSET,
        email_body: str = NOTSET  
    ) -> UsersRead:
        pass  # Декоратор делает всю работу!
    
    @get('/users/{id}', response_model=UsersRead)
    async def get_by_id(
        self,
        id_path: str
    ) -> UsersRead:
        pass
```

### TYPE_CHECKING imports

```python
# users_paginated.py
from __future__ import annotations

from pydantic import BaseModel
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from .users_read import UsersRead

class UsersPaginated(BaseModel):
    data: List["UsersRead"]  # Forward reference
    total: int

# model_rebuild() автоматически в models/__init__.py!
```

## ⚙️ Конфигурация

### Через openapi.toml

```toml
# Configuration for API client
url = "https://api.example.com/openapi.json"
```

### Через аргументы командной строки

```bash
python -m openapi_client.cli \
    --url https://api.example.com/openapi.json \
    --dirname my_awesome_client \
    --force
```

## 🔧 Продвинутые возможности

### Управление сессией

```python
client = ApiClient()

# Автоматическое обновление сессии при изменении headers
client.update_headers(Authorization="Bearer new_token")  # Сессия пересоздается

# Принудительное обновление
await client.refresh_session()

# Контекстное управление
async with client.with_headers(ApiVersion="v3"):
    # Запросы с временной версией API
    v3_data = await client.users.find_many()
# Автоматически возвращается к базовой версии

# Управление авторизацией
client.set_auth_token(token)  # Установка Bearer токена
client.remove_auth()          # Удаление авторизации
```

### Обработка ошибок

```python
from my_client.common import SendRequestError

try:
    users = await client.users.find_many()
except SendRequestError as e:
    print(f"API ошибка: {e.status_code} - {e.message}")
    print(f"Путь: {e.path}")
    print(f"Данные ответа: {e.response_data}")
```

## 📊 Технические детали

### Автоматическая обработка параметров

- **Query параметры**: `name_query` → `?name=value`
- **Path параметры**: `id_path` → `/users/{id_path}`  
- **Body параметры**: `data_body` → JSON body
- **File параметры**: `file_file` → multipart upload

### Поддержка content-types

- **application/json** → Автоматический парсинг в Pydantic модели
- **text/*** → Строки (CSV, HTML, plain text)
- **application/xml** → XML строки
- **application/octet-stream** → Binary данные (bytes)
- **Неизвестные форматы** → Умный fallback без ошибок

### Forward references

```python
# Автоматическое разрешение циклических зависимостей
class User(BaseModel):
    posts: List["Post"]  # Forward reference
    
class Post(BaseModel):  
    author: "User"       # Forward reference

# model_rebuild() вызывается автоматически в правильном порядке!
```

## 🤝 Разработка

### Требования

- Python 3.8+
- aiohttp
- pydantic>=2.0
- simple-singleton

### Запуск тестов

```bash
# Генерация тестовых клиентов
python -m openapi_client.cli --url tests/tap_openapi.json --dirname tests/tap_client
python -m openapi_client.cli --url tests/tbb_openapi.json --dirname tests/test_generated

# Запуск тестов
python tests/test_client.py
```

## ⭐ Ключевые преимущества

1. **🎯 Умная генерация** - анализирует схемы и создает интеллектуальные имена
2. **🔄 Современная архитектура** - FastAPI-style декораторы с полной обработкой  
3. **🛠️ Production-ready** - контекстное управление, обработка ошибок, типизация
4. **📦 Удобство использования** - автогенерация ссылок на модели, интуитивное API
5. **🔧 Универсальность** - поддержка любых content-types и OpenAPI спецификаций

## 📄 Лицензия

MIT License

## 🤝 Вклад в проект

Добро пожаловать! Создавайте issues и pull requests на [GitHub](https://github.com/PythonPackageArea/OpenApiClient.git).
