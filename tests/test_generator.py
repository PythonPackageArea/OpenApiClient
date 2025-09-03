"""
Тесты для генератора OpenAPI клиентов
"""

import pytest
from api_to_client.generator import ApiClientGenerator


class TestOpenApiClientGenerator:
    """Тесты основной функциональности генератора"""

    def test_simple_api_generation(self):
        """Тест генерации простого API"""
        simple_spec = {
            "openapi": "3.0.0",
            "info": {"title": "Test API", "version": "1.0.0"},
            "paths": {
                "/users": {
                    "get": {
                        "summary": "Get users",
                        "tags": ["users"],
                        "responses": {"200": {"description": "Success"}},
                    },
                    "post": {
                        "summary": "Create user",
                        "tags": ["users"],
                        "requestBody": {
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "name": {"type": "string"},
                                            "email": {"type": "string"},
                                        },
                                    }
                                }
                            }
                        },
                        "responses": {"201": {"description": "Created"}},
                    },
                },
                "/users/{user_id}": {
                    "get": {
                        "summary": "Get user",
                        "tags": ["users"],
                        "parameters": [
                            {
                                "name": "user_id",
                                "in": "path",
                                "required": True,
                                "schema": {"type": "integer"},
                            }
                        ],
                        "responses": {"200": {"description": "Success"}},
                    }
                },
            },
        }

        generator = ApiClientGenerator(simple_spec)
        project = generator.generate()

        # Проверяем что файлы созданы
        assert len(project.files) > 0

        # Проверяем наличие основных файлов
        file_names = [f.file_name for f in project.files]
        assert "client.py" in file_names
        assert "common.py" in file_names
        assert "lib/models.py" in file_names
        assert "endpoints/users.py" in file_names

        # Проверяем содержимое endpoints
        users_endpoint = None
        for f in project.files:
            if f.file_name == "endpoints/users.py":
                users_endpoint = str(f)
                break

        assert users_endpoint is not None
        assert "user_id_path" in users_endpoint  # path параметр
        assert "name_body" in users_endpoint  # body параметр
        assert "email_body" in users_endpoint  # body параметр

    def test_schemas_generation(self):
        """Тест генерации схем"""
        spec_with_schemas = {
            "openapi": "3.0.0",
            "info": {"title": "Test API", "version": "1.0.0"},
            "components": {
                "schemas": {
                    "User": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer"},
                            "name": {"type": "string"},
                            "email": {"type": "string", "format": "email"},
                            "created_at": {"type": "string", "format": "date-time"},
                        },
                        "required": ["id", "name"],
                    },
                    "UserStatus": {
                        "type": "string",
                        "enum": ["active", "inactive", "pending"],
                    },
                }
            },
            "paths": {
                "/users": {
                    "get": {
                        "tags": ["users"],
                        "responses": {
                            "200": {
                                "description": "Success",
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
                    }
                }
            },
        }

        generator = ApiClientGenerator(spec_with_schemas)
        project = generator.generate()

        # Проверяем модели
        models_file = None
        for f in project.files:
            if f.file_name == "models/users.py":
                models_file = str(f)
                break

        assert models_file is not None
        assert "class User(BaseModel)" in models_file
        assert "class Userstatus(str, Enum)" in models_file

    def test_multiple_tags_generation(self):
        """Тест генерации множественных тегов"""
        multi_tag_spec = {
            "openapi": "3.0.0",
            "info": {"title": "Multi Tag API", "version": "1.0.0"},
            "paths": {
                "/users": {
                    "get": {
                        "tags": ["users"],
                        "responses": {"200": {"description": "OK"}},
                    }
                },
                "/auth/login": {
                    "post": {
                        "tags": ["auth"],
                        "responses": {"200": {"description": "OK"}},
                    }
                },
                "/orders": {
                    "get": {
                        "tags": ["orders"],
                        "responses": {"200": {"description": "OK"}},
                    }
                },
            },
        }

        generator = ApiClientGenerator(multi_tag_spec)
        project = generator.generate()

        file_names = [f.file_name for f in project.files]

        # Проверяем что созданы файлы для каждого тега
        assert "endpoints/users.py" in file_names
        assert "endpoints/auth.py" in file_names
        assert "endpoints/orders.py" in file_names
        assert "models/users.py" in file_names
        assert "models/auth.py" in file_names
        assert "models/orders.py" in file_names

    def test_parameter_naming_conventions(self):
        """Тест правильного именования параметров"""
        param_spec = {
            "openapi": "3.0.0",
            "info": {"title": "Param Test API", "version": "1.0.0"},
            "paths": {
                "/items/{item_id}": {
                    "get": {
                        "tags": ["items"],
                        "parameters": [
                            {
                                "name": "item_id",
                                "in": "path",
                                "required": True,
                                "schema": {"type": "integer"},
                            },
                            {
                                "name": "include_details",
                                "in": "query",
                                "schema": {"type": "boolean"},
                            },
                            {
                                "name": "limit",
                                "in": "query",
                                "schema": {"type": "integer"},
                            },
                        ],
                        "responses": {"200": {"description": "OK"}},
                    },
                    "put": {
                        "tags": ["items"],
                        "parameters": [
                            {
                                "name": "item_id",
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
                                            "name": {"type": "string"},
                                            "description": {"type": "string"},
                                        },
                                    }
                                }
                            }
                        },
                        "responses": {"200": {"description": "OK"}},
                    },
                }
            },
        }

        generator = ApiClientGenerator(param_spec)
        project = generator.generate()

        items_endpoint = None
        for f in project.files:
            if f.file_name == "endpoints/items.py":
                items_endpoint = str(f)
                break

        assert items_endpoint is not None

        # Проверяем правильное именование параметров
        assert "item_id_path" in items_endpoint  # path параметр
        assert "include_details_query" in items_endpoint  # query параметр
        assert "limit_query" in items_endpoint  # query параметр
        assert "name_body" in items_endpoint  # body параметр
        assert "description_body" in items_endpoint  # body параметр

    def test_clean_endpoint_code(self):
        """Тест чистого кода endpoints с locals()"""
        spec = {
            "openapi": "3.0.0",
            "info": {"title": "Clean Code Test", "version": "1.0.0"},
            "paths": {
                "/test": {
                    "post": {
                        "tags": ["test"],
                        "requestBody": {
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {"data": {"type": "string"}},
                                    }
                                }
                            }
                        },
                        "responses": {"200": {"description": "OK"}},
                    }
                }
            },
        }

        generator = ApiClientGenerator(spec)
        project = generator.generate()

        test_endpoint = None
        for f in project.files:
            if f.file_name == "endpoints/test.py":
                test_endpoint = str(f)
                break

        assert test_endpoint is not None

        # Проверяем что используется locals()
        assert "locals().items()" in test_endpoint
        assert "k.endswith('_body')" in test_endpoint
        assert "models.is_not_set(v)" in test_endpoint

        # Проверяем правильные отступы
        lines = test_endpoint.split("\n")
        for line in lines:
            if "path = " in line and line.strip().startswith("path ="):
                # path должен иметь отступ в 8 пробелов от начала функции
                assert line.startswith(
                    "        "
                ), f"Неправильный отступ в строке: {line}"
