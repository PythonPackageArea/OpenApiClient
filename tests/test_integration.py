"""
Интеграционные тесты для генератора
"""

import tempfile
import os
from api_to_client.generator import ApiClientGenerator


class TestIntegration:
    """Интеграционные тесты"""

    def test_complete_generation_workflow(self):
        """Тест полного процесса генерации"""
        # Комплексная OpenAPI спецификация
        complex_spec = {
            "openapi": "3.0.0",
            "info": {"title": "Complex API", "version": "2.0.0"},
            "components": {
                "schemas": {
                    "User": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer"},
                            "username": {"type": "string"},
                            "email": {"type": "string", "format": "email"},
                            "created_at": {"type": "string", "format": "date-time"},
                            "is_active": {"type": "boolean"},
                        },
                        "required": ["id", "username", "email"],
                    },
                    "CreateUserRequest": {
                        "type": "object",
                        "properties": {
                            "username": {"type": "string"},
                            "email": {"type": "string"},
                            "password": {"type": "string"},
                        },
                        "required": ["username", "email", "password"],
                    },
                    "UserRole": {
                        "type": "string",
                        "enum": ["admin", "user", "moderator"],
                    },
                    "LoginResponse": {
                        "type": "object",
                        "properties": {
                            "access_token": {"type": "string"},
                            "token_type": {"type": "string"},
                            "user": {"$ref": "#/components/schemas/User"},
                        },
                    },
                }
            },
            "paths": {
                "/auth/login": {
                    "post": {
                        "tags": ["authentication"],
                        "summary": "User login",
                        "requestBody": {
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "username": {"type": "string"},
                                            "password": {"type": "string"},
                                        },
                                    }
                                }
                            }
                        },
                        "responses": {
                            "200": {
                                "description": "Successful login",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "$ref": "#/components/schemas/LoginResponse"
                                        }
                                    }
                                },
                            },
                            "401": {"description": "Invalid credentials"},
                        },
                    }
                },
                "/users": {
                    "get": {
                        "tags": ["users"],
                        "summary": "Get all users",
                        "parameters": [
                            {
                                "name": "limit",
                                "in": "query",
                                "schema": {"type": "integer"},
                            },
                            {
                                "name": "offset",
                                "in": "query",
                                "schema": {"type": "integer"},
                            },
                            {
                                "name": "search",
                                "in": "query",
                                "schema": {"type": "string"},
                            },
                        ],
                        "responses": {
                            "200": {
                                "description": "Users list",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "array",
                                            "items": {
                                                "$ref": "#/components/schemas/User"
                                            },
                                        }
                                    }
                                },
                            }
                        },
                    },
                    "post": {
                        "tags": ["users"],
                        "summary": "Create user",
                        "requestBody": {
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/CreateUserRequest"
                                    }
                                }
                            }
                        },
                        "responses": {
                            "201": {
                                "description": "User created",
                                "content": {
                                    "application/json": {
                                        "schema": {"$ref": "#/components/schemas/User"}
                                    }
                                },
                            }
                        },
                    },
                },
                "/users/{user_id}": {
                    "get": {
                        "tags": ["users"],
                        "summary": "Get user by ID",
                        "parameters": [
                            {
                                "name": "user_id",
                                "in": "path",
                                "required": True,
                                "schema": {"type": "integer"},
                            }
                        ],
                        "responses": {
                            "200": {
                                "description": "User details",
                                "content": {
                                    "application/json": {
                                        "schema": {"$ref": "#/components/schemas/User"}
                                    }
                                },
                            },
                            "404": {"description": "User not found"},
                        },
                    },
                    "put": {
                        "tags": ["users"],
                        "summary": "Update user",
                        "parameters": [
                            {
                                "name": "user_id",
                                "in": "path",
                                "required": True,
                                "schema": {"type": "integer"},
                            }
                        ],
                        "requestBody": {
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "username": {"type": "string"},
                                            "email": {"type": "string"},
                                        },
                                    }
                                }
                            }
                        },
                        "responses": {
                            "200": {
                                "description": "User updated",
                                "content": {
                                    "application/json": {
                                        "schema": {"$ref": "#/components/schemas/User"}
                                    }
                                },
                            }
                        },
                    },
                    "delete": {
                        "tags": ["users"],
                        "summary": "Delete user",
                        "parameters": [
                            {
                                "name": "user_id",
                                "in": "path",
                                "required": True,
                                "schema": {"type": "integer"},
                            }
                        ],
                        "responses": {
                            "204": {"description": "User deleted"},
                            "404": {"description": "User not found"},
                        },
                    },
                },
                "/users/{user_id}/avatar": {
                    "post": {
                        "tags": ["users"],
                        "summary": "Upload user avatar",
                        "parameters": [
                            {
                                "name": "user_id",
                                "in": "path",
                                "required": True,
                                "schema": {"type": "integer"},
                            }
                        ],
                        "requestBody": {
                            "content": {
                                "multipart/form-data": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "avatar": {
                                                "type": "string",
                                                "format": "binary",
                                            }
                                        },
                                    }
                                }
                            }
                        },
                        "responses": {"200": {"description": "Avatar uploaded"}},
                    }
                },
            },
        }

        generator = ApiClientGenerator(complex_spec)
        project = generator.generate()

        # Проверяем структуру проекта
        file_names = [f.file_name for f in project.files]

        # Основные файлы
        assert "client.py" in file_names
        assert "common.py" in file_names
        assert "__init__.py" in file_names
        assert "py.typed" in file_names
        assert "lib/models.py" in file_names
        assert "lib/exc.py" in file_names

        # Endpoints по тегам
        assert "endpoints/authentication.py" in file_names
        assert "endpoints/users.py" in file_names
        assert "endpoints/__init__.py" in file_names

        # Models по тегам
        assert "models/authentication.py" in file_names
        assert "models/users.py" in file_names
        assert "models/__init__.py" in file_names

        # Проверяем содержимое endpoints/users.py
        users_endpoint = None
        for f in project.files:
            if f.file_name == "endpoints/users.py":
                users_endpoint = str(f)
                break

        assert users_endpoint is not None

        # Проверяем методы (функции генерируются автоматически с разными именами)
        assert "async def " in users_endpoint
        assert "user_id_path" in users_endpoint  # path параметр
        assert "limit_query" in users_endpoint  # query параметр
        assert "username_body" in users_endpoint  # body параметр
        assert "avatar_file" in users_endpoint  # file параметр

        # Проверяем правильные отступы в коде
        lines = users_endpoint.split("\n")
        path_line_found = False
        for line in lines:
            if line.strip().startswith("path ="):
                path_line_found = True
                # path должен начинаться с 8 пробелов от начала функции
                assert line.startswith(
                    "        "
                ), f"Неправильный отступ path: '{line}'"
        assert path_line_found, "Строка с path = не найдена"

        # Проверяем содержимое models/users.py
        users_models = None
        for f in project.files:
            if f.file_name == "models/users.py":
                users_models = str(f)
                break

        assert users_models is not None
        assert "class User(BaseModel)" in users_models
        assert "class Createuserrequest(BaseModel)" in users_models
        assert "class Userrole(str, Enum)" in users_models

    def test_file_generation_and_save(self):
        """Тест генерации и сохранения файлов"""
        simple_spec = {
            "openapi": "3.0.0",
            "info": {"title": "Save Test", "version": "1.0.0"},
            "paths": {
                "/ping": {
                    "get": {
                        "tags": ["health"],
                        "responses": {"200": {"description": "Pong"}},
                    }
                }
            },
        }

        generator = ApiClientGenerator(simple_spec)
        project = generator.generate()

        with tempfile.TemporaryDirectory() as temp_dir:
            # Сохраняем файлы
            for file_model in project.files:
                file_path = os.path.join(temp_dir, file_model.file_name)
                os.makedirs(os.path.dirname(file_path), exist_ok=True)

                with open(file_path, "w") as f:
                    f.write(str(file_model))

            # Проверяем что файлы созданы
            assert os.path.exists(os.path.join(temp_dir, "client.py"))
            assert os.path.exists(os.path.join(temp_dir, "endpoints", "health.py"))

            # Проверяем содержимое
            with open(os.path.join(temp_dir, "endpoints", "health.py"), "r") as f:
                content = f.read()
                assert "class Health:" in content
                assert "async def" in content
