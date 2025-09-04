import re
from typing import Dict, Any, List, Optional

from ..types.models import (
    Project,
    CodeBlock,
    CodeFile,
    Class,
    Function,
    Parameter,
    Variable,
)
from ..types.schema_resolver import SchemaNameResolver
from .templates import templates
from .http_client import aiohttp_common


class ClientGenerator:
    """Генератор API клиента из OpenAPI"""

    def __init__(self, openapi_dict: Dict[str, Any], source_url: str = None):
        self.openapi_dict = openapi_dict
        self.source_url = source_url
        self.project = Project(name="api")
        self.schema_resolver = SchemaNameResolver()
        self.zones = {}  # zone_name -> {endpoints_file, models_file}
        self.used_schemas = set()  # Только используемые схемы

    def generate(self) -> Project:
        """Основная генерация"""
        self._create_base_files()
        self._register_all_schemas()  # ОТКАТ: регистрируем ВСЕ схемы
        self._generate_schemas()
        self._generate_endpoints()
        self._finalize_structure()
        return self.project

    def _collect_used_schemas(self):
        """Сбор только используемых схем из responses endpoints"""
        # Собираем схемы из responses
        for path, path_spec in self.openapi_dict.get("paths", {}).items():
            for method, method_spec in path_spec.items():
                self._collect_schemas_from_responses(method_spec.get("responses", {}))

        # Рекурсивно собираем зависимые схемы
        self._collect_dependent_schemas()

        # Регистрируем все найденные схемы
        self._register_used_schemas()

    def _collect_schemas_from_responses(self, responses: Dict):
        """Сбор схем из responses"""
        for status_code, response_spec in responses.items():
            if status_code.startswith("2"):  # Только успешные ответы
                content = response_spec.get("content", {})
                for content_type, content_spec in content.items():
                    schema = content_spec.get("schema", {})
                    self._extract_schema_refs(schema)

    def _extract_schema_refs(self, schema: Dict):
        """Рекурсивное извлечение всех $ref из схемы"""
        if "$ref" in schema:
            ref_name = schema["$ref"].replace("#/components/schemas/", "")
            self.used_schemas.add(ref_name)
        elif schema.get("type") == "array" and "items" in schema:
            self._extract_schema_refs(schema["items"])
        elif schema.get("anyOf") or schema.get("oneOf"):
            variants = schema.get("anyOf", []) + schema.get("oneOf", [])
            for variant in variants:
                self._extract_schema_refs(variant)
        elif schema.get("type") == "object" and "properties" in schema:
            for prop_spec in schema["properties"].values():
                self._extract_schema_refs(prop_spec)

    def _collect_dependent_schemas(self):
        """Рекурсивно собираем зависимые схемы"""
        schemas = self.openapi_dict.get("components", {}).get("schemas", {})
        to_process = list(self.used_schemas)

        while to_process:
            schema_name = to_process.pop()
            if schema_name in schemas:
                schema_spec = schemas[schema_name]
                # Ищем зависимости в этой схеме
                dependencies = set()
                self._find_schema_dependencies(schema_spec, dependencies)

                # Добавляем новые зависимости
                for dep in dependencies:
                    if dep not in self.used_schemas:
                        self.used_schemas.add(dep)
                        to_process.append(dep)

    def _find_schema_dependencies(self, schema: Dict, dependencies: set):
        """Находим все зависимости схемы"""
        if "$ref" in schema:
            ref_name = schema["$ref"].replace("#/components/schemas/", "")
            dependencies.add(ref_name)
        elif isinstance(schema, dict):
            for value in schema.values():
                if isinstance(value, dict):
                    self._find_schema_dependencies(value, dependencies)
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, dict):
                            self._find_schema_dependencies(item, dependencies)

    def _register_all_schemas(self):
        """Регистрация всех схем для правильного разрешения имен"""
        schemas = self.openapi_dict.get("components", {}).get("schemas", {})

        for schema_name, schema_spec in schemas.items():

            zone = self._determine_zone(schema_name)
            clean_name = self._get_clean_schema_name(schema_name)
            self.schema_resolver.register_schema(schema_name, clean_name, zone)

    def _create_base_files(self):
        """Создание базовых файлов проекта"""
        # Основные файлы
        self.project.add_file("common.py").add_code_block(
            CodeBlock(code=aiohttp_common)
        )
        self.project.add_file("client.py").add_code_block(
            CodeBlock(code=templates.client)
        )
        self.project.add_file("lib/models.py").add_code_block(
            CodeBlock(code=templates.lib_models)
        )
        self.project.add_file("lib/exc.py").add_code_block(
            CodeBlock(code=templates.lib_exc)
        )
        self.project.add_file("lib/__init__.py").add_code_block(CodeBlock(code=""))
        self.project.add_file("py.typed").add_code_block(CodeBlock(code="# PEP 561"))

        # Production файлы
        self.project.add_file("requirements.txt").add_code_block(
            CodeBlock(code="aiohttp>=3.8.0\npydantic>=2.0.0\nsimple-singleton>=1.0.0")
        )
        self.project.add_file(".gitignore").add_code_block(
            CodeBlock(
                code="__pycache__/\n*.pyc\n*.pyo\n.env\n.venv/\n.pytest_cache/\nopenapi.toml"
            )
        )

        # Конфиг файл в папке клиента
        if self.source_url:
            config_content = (
                f'# Configuration for API client\nurl = "{self.source_url}"\n'
            )
            self.project.add_file("openapi.toml").add_code_block(
                CodeBlock(code=config_content)
            )

    def _generate_schemas(self):
        """Генерация всех Pydantic моделей из components/schemas"""
        schemas = self.openapi_dict.get("components", {}).get("schemas", {})

        for schema_name, schema_spec in schemas.items():

            zone = self._determine_zone(schema_name)
            clean_name = self._get_clean_schema_name(schema_name)

            # Создаем файл зоны если нужно
            self._ensure_zone(zone)

            # Генерируем модель
            self._generate_model(clean_name, schema_spec, zone)

    def _generate_endpoints(self):
        """Генерация endpoints по тегам"""
        for path, path_spec in self.openapi_dict.get("paths", {}).items():
            for method, method_spec in path_spec.items():
                zone = self._get_endpoint_zone(method_spec)
                self._ensure_zone(zone)
                self._generate_endpoint_method(path, method, method_spec, zone)

    def _generate_endpoint_method(self, path: str, method: str, spec: Dict, zone: str):
        """Генерация метода endpoint с чистым кодом через locals()"""
        zone_class = self.zones[zone]["endpoints_class"]

        # Генерируем имя функции
        func_name = self._generate_function_name(path, method, spec)

        # Параметры
        parameters = [Parameter(name="self")]
        for param_spec in spec.get("parameters", []):
            param = self._create_parameter(param_spec)
            parameters.append(param)

        # Body параметры
        request_body = spec.get("requestBody", {})
        if request_body:
            body_params = self._create_body_parameters(request_body, zone)
            parameters.extend(body_params)

        # Тип возврата
        return_type = self._get_return_type(spec.get("responses", {}), zone)

        # Создаем функцию с чистым кодом
        func = zone_class.add_function(
            func_name,
            parameters=parameters,
            async_def=True,
            response=return_type,
            description=spec.get("description", ""),
        )

        # Генерируем чистый код через locals()
        code = self._generate_clean_endpoint_code(path, method, spec, zone)
        func.code = CodeBlock(code=code)

    def _generate_clean_endpoint_code(
        self, path: str, method: str, spec: Dict, zone: str
    ) -> str:
        """Генерация чистого кода endpoint через locals()"""
        code_lines = []

        # Путь с подстановкой параметров
        if "{" in path:
            # Находим все {param} в пути и заменяем на param_path переменные
            import re

            path_template = path
            path_params = re.findall(r"\{(\w+)\}", path)
            for param in path_params:
                path_template = path_template.replace(
                    f"{{{param}}}", f"{{{param}_path}}"
                )

            code_lines.append(f"path = f'{path_template}'.rstrip()")
        else:
            code_lines.append(f"path = '{path}'.rstrip()")

        # Query параметры
        code_lines.append("params = self._prepare_params(locals())")

        # Body параметры с автоматической конвертацией моделей
        code_lines.append("data = self._prepare_body_data(locals())")

        # Files параметры
        code_lines.append("files = self._prepare_files(locals())")



        # HTTP запрос
        code_lines.append(f"return await self._handle_request('{method}', path, params, data, files)")

        return "\n".join(code_lines)

    def _generate_response_handling(self, responses: Dict, zone: str) -> List[str]:
        """Генерация обработки ответов с новой логикой"""
        code_lines = []

        code_lines.append("if not hasattr(response, 'status_code'):")
        code_lines.append("    return response")
        code_lines.append("")
        code_lines.append("data = await response.json()")

        # Ищем успешные ответы и извлекаем модель
        model_name = None
        has_null = False

        for status_code, response_spec in responses.items():
            if status_code.startswith("2"):
                content = response_spec.get("content", {})
                if content:
                    for content_type, content_spec in content.items():
                        schema = content_spec.get("schema", {})

                        # Обработка anyOf/oneOf (например, LoginResponse | null)
                        if schema.get("anyOf") or schema.get("oneOf"):
                            variants = schema.get("anyOf", []) + schema.get("oneOf", [])

                            for variant in variants:
                                if "$ref" in variant:
                                    model_ref = variant["$ref"].replace(
                                        "#/components/schemas/", ""
                                    )
                                    model_name = (
                                        self.schema_resolver.resolve_schema_name(
                                            model_ref, zone
                                        )
                                    )
                                elif (
                                    variant.get("type") == "object"
                                    and "title" in variant
                                ):
                                    title = variant["title"]
                                    model_name = (
                                        self.schema_resolver.resolve_schema_name(
                                            title, zone
                                        )
                                    )
                                elif variant.get("type") == "null":
                                    has_null = True

                        elif "$ref" in schema:
                            # Прямая ссылка на модель
                            ref_name = schema["$ref"].replace(
                                "#/components/schemas/", ""
                            )
                            model_name = self.schema_resolver.resolve_schema_name(
                                ref_name, zone
                            )

                        elif schema.get("type") == "array" and "items" in schema:
                            # Массив моделей
                            items = schema["items"]
                            if "$ref" in items:
                                ref_name = items["$ref"].replace(
                                    "#/components/schemas/", ""
                                )
                                item_model = self.schema_resolver.resolve_schema_name(
                                    ref_name, zone
                                )
                                model_name = f"[{item_model}(**item) for item in data]"
                                # Специальная обработка для массивов
                                code_lines.append("try:")
                                code_lines.append(f"    return {model_name}")
                                code_lines.append("except Exception:")
                                code_lines.append("    pass")
                                code_lines.append("")
                                code_lines.append("return data")
                                return code_lines

                        elif schema.get("type") == "object" and "title" in schema:
                            # Инлайн объект с title
                            title = schema["title"]
                            model_name = self.schema_resolver.resolve_schema_name(
                                title, zone
                            )

                        if model_name and not model_name.startswith("["):
                            break
                    if model_name:
                        break

        # Генерируем финальную обработку
        if model_name and not model_name.startswith("["):
            code_lines.append("try:")
            if has_null:
                code_lines.append(
                    f"    return {model_name}(**data) if data is not None else None"
                )
            else:
                code_lines.append(f"    return {model_name}(**data)")
            code_lines.append("except Exception:")
            code_lines.append("    pass")

        code_lines.append("")
        code_lines.append("return data")

        return code_lines

    def _create_parameter(self, param_spec: Dict) -> Parameter:
        """Создание параметра с правильным именованием"""
        name = param_spec["name"]
        param_type = param_spec["in"]

        if param_type == "path":
            param_name = f"{name}_path"
        elif param_type == "query":
            param_name = f"{name}_query"
        else:
            param_name = name

        var_type = self._get_type(param_spec.get("schema", {}), "")

        default = None
        if not param_spec.get("required", False):
            default = Variable(value="models.NOTSET")

        return Parameter(name=param_name, var_type=var_type, default=default)

    def _create_body_parameters(
        self, request_body: Dict, zone: str = ""
    ) -> List[Parameter]:
        """Создание body параметров с поддержкой моделей"""
        parameters = []
        content = request_body.get("content", {})

        for content_type, content_spec in content.items():
            schema = content_spec.get("schema", {})

            # Если schema ссылается на модель напрямую
            if "$ref" in schema:
                ref_name = schema["$ref"].replace("#/components/schemas/", "")
                # Для body параметров используем глобальное разрешение
                clean_name = self._get_clean_schema_name(ref_name)
                param_name = "request_body"
                var_type = Variable(value=f'"{clean_name}"')
                default = Variable(value="models.NOTSET")

                parameters.append(
                    Parameter(name=param_name, var_type=var_type, default=default)
                )
            else:
                # Обработка properties
                properties = schema.get("properties", {})

                for prop_name, prop_spec in properties.items():
                    if content_type == "multipart/form-data":
                        param_name = f"{prop_name}_file"
                    else:
                        param_name = f"{prop_name}_body"

                    # Для body параметров используем метод для endpoint параметров
                    var_type = self._get_type_for_endpoint_parameter(prop_spec)
                    default = Variable(value="models.NOTSET")

                    parameters.append(
                        Parameter(name=param_name, var_type=var_type, default=default)
                    )

        return parameters

    def _get_type(self, schema: Dict, zone: str = "") -> Variable:
        """Получение типа из схемы"""
        if "$ref" in schema:
            ref_name = schema["$ref"].replace("#/components/schemas/", "")
            clean_name = self.schema_resolver.resolve_schema_name(ref_name, zone)
            return Variable(value=clean_name)

        schema_type = schema.get("type", "string")
        format_type = schema.get("format")

        type_mapping = {
            "string": "str",
            "integer": "int",
            "boolean": "bool",
            "number": "float",
            "array": "list",
            "object": "dict",
        }

        if format_type == "date-time":
            return Variable(value="datetime")
        elif format_type in ["binary", "byte"]:
            return Variable(value="bytes")

        base_type = type_mapping.get(schema_type, "str")

        if schema.get("enum"):
            enum_values = [repr(v) for v in schema["enum"]]
            return Variable(value=enum_values, wrap_name="Literal")

        if schema_type == "array" and "items" in schema:
            item_type = self._get_type(schema["items"], zone)
            return Variable(value=item_type, wrap_name="List")

        return Variable(value=base_type)

    def _get_return_type(self, responses: Dict, zone: str) -> str:
        """Получение типа возврата с правильными моделями"""
        success_responses = []

        for status_code, response_spec in responses.items():
            if status_code.startswith("2"):
                content = response_spec.get("content", {})
                if content:
                    for content_type, content_spec in content.items():
                        schema = content_spec.get("schema", {})

                        # Обработка anyOf/oneOf структур (например, LoginResponse | null)
                        if schema.get("anyOf") or schema.get("oneOf"):
                            variants = schema.get("anyOf", []) + schema.get("oneOf", [])
                            type_variants = []
                            has_null = False

                            for variant in variants:
                                if "$ref" in variant:
                                    ref_name = variant["$ref"].replace(
                                        "#/components/schemas/", ""
                                    )
                                    clean_name = (
                                        self.schema_resolver.resolve_schema_name(
                                            ref_name, zone
                                        )
                                    )
                                    type_variants.append(clean_name)
                                elif variant.get("type") == "null":
                                    has_null = True
                                elif (
                                    variant.get("type") == "object"
                                    and "title" in variant
                                ):
                                    # Это развернутая схема с title - ищем зарегистрированную схему
                                    title = variant["title"]
                                    possible_name = f"{zone.capitalize()}{title}"
                                    # Проверяем есть ли зарегистрированная схема
                                    found = False
                                    for (
                                        registered_name,
                                        info,
                                    ) in self.schema_resolver._schema_registry.items():
                                        if info["clean_name"] == possible_name:
                                            type_variants.append(possible_name)
                                            found = True
                                            break
                                    if not found:
                                        clean_name = (
                                            self.schema_resolver.resolve_schema_name(
                                                title, zone
                                            )
                                        )
                                        type_variants.append(clean_name)
                                else:
                                    var_type = self._get_type(variant, zone)
                                    type_variants.append(str(var_type))

                            if len(type_variants) == 1:
                                result_type = type_variants[0]
                                if has_null:
                                    result_type = f"Optional[{result_type}]"
                                success_responses.append(result_type)
                            elif len(type_variants) > 1:
                                if has_null:
                                    success_responses.append(
                                        f"Optional[Union[{', '.join(type_variants)}]]"
                                    )
                                else:
                                    success_responses.append(
                                        f"Union[{', '.join(type_variants)}]"
                                    )

                        elif "$ref" in schema:
                            # Прямая ссылка на модель
                            ref_name = schema["$ref"].replace(
                                "#/components/schemas/", ""
                            )
                            clean_name = self.schema_resolver.resolve_schema_name(
                                ref_name, zone
                            )
                            success_responses.append(clean_name)
                        elif schema.get("type") == "array" and "items" in schema:
                            # Массив моделей
                            items = schema["items"]
                            if "$ref" in items:
                                ref_name = items["$ref"].replace(
                                    "#/components/schemas/", ""
                                )
                                clean_name = self.schema_resolver.resolve_schema_name(
                                    ref_name, zone
                                )
                                success_responses.append(f"List[{clean_name}]")
                            else:
                                var_type = self._get_type(schema, zone)
                                success_responses.append(str(var_type))
                        elif schema.get("type") == "object" and "title" in schema:
                            # Инлайн объект с title - пытаемся найти зарегистрированную схему
                            title = schema["title"]
                            # Ищем по зоне + title (например AccountsPaginated для зоны accounts + title Paginated)
                            possible_name = f"{zone.capitalize()}{title}"
                            # Проверяем есть ли такая зарегистрированная схема
                            for (
                                registered_name,
                                info,
                            ) in self.schema_resolver._schema_registry.items():
                                if info["clean_name"] == possible_name:
                                    success_responses.append(possible_name)
                                    break
                            else:
                                # Если не найдена, используем просто title
                                clean_name = self.schema_resolver.resolve_schema_name(
                                    title, zone
                                )
                                success_responses.append(clean_name)
                        else:
                            var_type = self._get_type(schema, zone)
                            success_responses.append(str(var_type))

        if len(success_responses) == 1:
            return success_responses[0]
        elif len(success_responses) > 1:
            return f"Union[{', '.join(success_responses)}]"
        else:
            return "Any"

    def _generate_function_name(self, path: str, method: str, spec: Dict) -> str:
        """Универсальная генерация имени функции"""
        summary = spec.get("summary", "")
        if summary:
            return re.sub(r"[^a-zA-Z0-9]", "_", summary.lower())

        # Генерация из пути
        path_parts = [p for p in path.strip("/").split("/") if p and "{" not in p]
        if path_parts:
            return f"{method}_{path_parts[0]}"
        return method

    def _determine_zone(self, schema_name: str) -> str:
        """Определение зоны для схемы"""
        schema_lower = schema_name.lower()

        # Body модели - определяем зону по содержимому имени
        if schema_name.startswith("Body"):
            # Например: BodyUpdateManySessionsUpdateManyPut -> sessions
            if "sessions" in schema_lower:
                return "sessions"
            elif "uploads" in schema_lower:
                return "uploads"
            elif "accounts" in schema_lower:
                return "accounts"
            elif "auth" in schema_lower:
                return "authentication"
            elif "groups" in schema_lower:
                return "groups"
            elif "exports" in schema_lower:
                return "exports"
            elif "settings" in schema_lower:
                return "settings"
            else:
                return "common"

        # FastAPI структура
        if "__services__" in schema_name:
            parts = schema_name.split("__")
            if len(parts) >= 4 and parts[2] == "services":
                return parts[3]  # users, bots, broadcasts, etc
            elif len(parts) >= 3:
                return parts[2]  # accounts, sessions, etc для старых форматов

        # Особые схемы по именам
        specific_mappings = {
            "signupin": "authentication",
            "keys": "settings",
            "lastaction": "accounts",
            "response": "uploads",  # Часто используется для upload статуса
            "inputstrings": "uploads",
        }

        if schema_lower in specific_mappings:
            return specific_mappings[schema_lower]

        # Глобальные схемы (ошибки)
        global_schemas = ["httperror", "validationerror", "httpvalidationerror"]
        if any(global_schema in schema_lower for global_schema in global_schemas):
            return "common"

        # По ключевым словам
        for keywords, zone in [
            (["auth", "login", "user", "signup"], "authentication"),
            (["account"], "accounts"),
            (["session"], "sessions"),
            (["upload"], "uploads"),
            (["group"], "groups"),
            (["export"], "exports"),
            (["setting", "key"], "settings"),
            (["module", "task"], "module_tasks"),
        ]:
            if any(keyword in schema_lower for keyword in keywords):
                return zone

        return "common"

    def _get_endpoint_zone(self, method_spec: Dict) -> str:
        """Получение зоны для endpoint"""
        tags = method_spec.get("tags", [])
        if tags:
            return self._snake_case(tags[0])
        return "default"

    def _ensure_zone(self, zone: str):
        """Создание файлов зоны если нужно"""
        if zone not in self.zones:
            # endpoints/<zone>.py
            endpoints_file = self.project.add_file(f"endpoints/{zone}.py")
            endpoints_file.imports.extend(
                [
                    "from ..lib import models",
                    "from ..common import AiohttpClient",
                    "from typing import Union, Optional, List, Literal, Any",
                    "from datetime import datetime",
                ]
            )

            # Добавляем импорт моделей для данной зоны
            models_import = f"from ..models.{zone} import *"
            endpoints_file.imports.append(models_import)

            # Добавляем импорт общих схем только если есть модели в common
            if any(
                info["zone"] == "common"
                for info in self.schema_resolver._schema_registry.values()
            ):
                endpoints_file.imports.append("from ..models.common import *")

            # Добавляем импорты других зон для body параметров
            other_zones = set()
            for schema_name, info in self.schema_resolver._schema_registry.items():
                schema_zone = info["zone"]
                if schema_zone != zone and schema_zone != "common":
                    other_zones.add(schema_zone)

            for other_zone in sorted(other_zones):
                endpoints_file.imports.append(f"from ..models.{other_zone} import *")

            # Кросс-импорты уже добавлены выше

            zone_class = endpoints_file.add_class(zone.capitalize())

            # Добавляем модели как атрибуты класса
            self._add_model_attributes_to_zone(zone_class, zone)

            zone_class.add_function(
                "__init__",
                parameters=[
                    Parameter(name="self"),
                    Parameter(name="client", var_type=Variable(value="AiohttpClient")),
                ],
                code=CodeBlock(code="self.client = client"),
            )
            
            # Добавляем хелпер методы для чистоты endpoints
            self._add_helper_methods(zone_class)

            # models/<zone>.py
            models_file = self.project.add_file(f"models/{zone}.py")
            models_file.imports.extend(
                [
                    "from pydantic import BaseModel",
                    "from enum import Enum",
                    "from typing import Optional, Union, List, Dict, Literal, Any, TYPE_CHECKING",
                    "from datetime import datetime",
                ]
            )

            # Добавляем кросс-импорты для других зон
            self._add_model_cross_imports(models_file, zone)

            self.zones[zone] = {
                "endpoints_file": endpoints_file,
                "endpoints_class": zone_class,
                "models_file": models_file,
            }

    def _generate_model(self, name: str, schema_spec: Dict, zone: str):
        """Генерация Pydantic модели"""
        models_file = self.zones[zone]["models_file"]

        if schema_spec.get("enum"):
            # Enum модель
            model_class = models_file.add_class(name, inherits=["str", "Enum"])
            for enum_value in schema_spec["enum"]:
                model_class.parameters.append(
                    Parameter(
                        name=str(enum_value).upper(),
                        default=Variable(value=repr(enum_value)),
                    )
                )
        else:
            # Обычная модель
            model_class = models_file.add_class(name, inherits=["BaseModel"])

            properties = schema_spec.get("properties", {})
            required = schema_spec.get("required", [])

            for field_name, field_spec in properties.items():
                field_type = self._get_type_for_model_field(field_spec, zone)

                # Делаем Optional если не required
                if field_name not in required:
                    if field_type.wrap_name != "Optional":
                        field_type = Variable(value=field_type, wrap_name="Optional")
                    default = Variable(value="None")
                else:
                    default = None

                model_class.parameters.append(
                    Parameter(name=field_name, var_type=field_type, default=default)
                )

    def _get_clean_schema_name(self, schema_name: str) -> str:
        """Получение чистого имени схемы"""
        return self.schema_resolver._clean_schema_name(schema_name)

    def _finalize_structure(self):
        """Финализация структуры проекта"""
        # Убираем model_rebuild() - не нужны при использовании только локальных ссылок

        # Создаем динамический client.py с прямым доступом к зонам
        self._generate_dynamic_client()

        # models/__init__.py
        models_init = self.project.add_file("models/__init__.py")
        for zone_name in self.zones.keys():
            models_init.imports.append(f"from . import {zone_name}")
        models_init.add_code_block(
            CodeBlock(code=f"__all__ = {list(self.zones.keys())}")
        )

        # Главный __init__.py
        main_init = self.project.add_file("__init__.py")
        main_init.imports.extend(
            [
                "from .client import ApiClient",
                "from . import models",
            ]
        )
        main_init.add_code_block(CodeBlock(code='__all__ = ["ApiClient", "models"]'))

    def _generate_dynamic_client(self):
        """Генерация клиента с прямым доступом к зонам"""
        # Подготавливаем данные для шаблона
        zone_imports = []
        zone_assignments = []

        for zone_name in self.zones.keys():
            zone_class = zone_name.capitalize()

            # TYPE_CHECKING импорты (без отступов - они добавятся в шаблоне)
            zone_imports.append(f"    from .endpoints.{zone_name} import {zone_class}")

            # Присваивание в __init__ (без отступов)
            zone_assignments.append(
                f'        self.{zone_name}: "{zone_class}" = {zone_class}(self)'
            )

        # Добавляем _api_url в присваивания
        if self.source_url:
            zone_assignments.append(f"        self._api_url: str = '{self.source_url}'")

        # Production готовность
        zone_assignments.extend(
            [
                "        self._timeout: int = 30",
                "        self._max_retries: int = 3",
                "        self._retry_delay: float = 1.0",
            ]
        )

        # Формируем шаблон
        client_template = templates.client.format(
            zone_imports="\n".join(zone_imports),
            zone_assignments="\n".join(zone_assignments),
        )

        # Заменяем client.py
        for file in self.project.files:
            if file.file_name == "client.py":
                file.code_blocks = [CodeBlock(code=client_template)]
                # Добавляем runtime импорты зон
                file.imports = []
                for zone_name in self.zones.keys():
                    zone_class = zone_name.capitalize()
                    file.imports.append(
                        f"from .endpoints.{zone_name} import {zone_class}"
                    )
                break

    @staticmethod
    def _snake_case(name: str) -> str:
        return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()

    @staticmethod
    def _pascal_case(name: str) -> str:
        """Правильное PascalCase преобразование"""
        if not name:
            return ""

        # Убираем спецсимволы и разбиваем
        clean = re.sub(r"[^a-zA-Z0-9]", "_", name)
        parts = []

        for part in clean.split("_"):
            if not part:
                continue

            # Особые случаи для аббревиатур
            if part.upper() in ["HTTP", "API", "URL", "JSON", "XML", "HTML", "ID"]:
                parts.append(part.upper())
            elif part.lower() in ["id"]:
                parts.append("ID")
            else:
                # Обычное PascalCase
                parts.append(part.capitalize())

        return "".join(parts)

    def _add_model_attributes_to_zone(self, zone_class: Class, zone: str):
        """Добавление моделей как атрибутов класса зоны"""
        # Находим все модели этой зоны
        zone_models = []
        for schema_name, info in self.schema_resolver._schema_registry.items():
            if info["zone"] == zone:
                clean_name = info["clean_name"]
                # Создаем snake_case версию для атрибута
                attr_name = self._snake_case(clean_name)
                zone_models.append((attr_name, clean_name))

        # Добавляем как параметры класса (атрибуты)
        for attr_name, clean_name in zone_models:
            zone_class.parameters.append(
                Parameter(
                    name=attr_name,
                    var_type=Variable(value=clean_name),
                    default=Variable(value=clean_name),
                )
            )

    def _get_type(self, schema: Dict, zone: str = "") -> Variable:
        """Получение типа из OpenAPI схемы с правильными $ref"""
        if not schema:
            return Variable(value="Any")

        # $ref ссылки - правильно разрешаем в контексте зоны
        if "$ref" in schema:
            ref_name = schema["$ref"].replace("#/components/schemas/", "")
            resolved_name = self.schema_resolver.resolve_schema_name(
                ref_name,
                zone,
            )
            return Variable(value=resolved_name)

        schema_type = schema.get("type", "string")
        format_type = schema.get("format")

        # Базовые типы
        type_mapping = {
            "string": "str",
            "integer": "int",
            "boolean": "bool",
            "number": "float",
            "object": "dict",
            "null": "None",
        }

        # Форматы
        if format_type in ["date-time", "datetime"]:
            return Variable(value="datetime")
        elif format_type in ["binary", "byte"]:
            return Variable(value="bytes")
        elif format_type == "date":
            return Variable(value="date")

        # Enum
        if schema.get("enum"):
            enum_values = [repr(v) for v in schema["enum"]]
            return Variable(value=enum_values, wrap_name="Literal")

        # Array
        if schema_type == "array":
            items_schema = schema.get("items", {})
            item_type = self._get_type(items_schema, zone)
            return Variable(value=item_type, wrap_name="List")

        # anyOf/oneOf - правильная обработка Union типов
        if schema.get("anyOf") or schema.get("oneOf"):
            variants = schema.get("anyOf", []) + schema.get("oneOf", [])
            types = []
            has_null = False

            for variant in variants:
                if variant.get("type") == "null":
                    has_null = True
                elif "$ref" in variant:
                    # $ref в anyOf
                    ref_name = variant["$ref"].replace("#/components/schemas/", "")
                    # Проверяем что схема зарегистрирована (не Body модель)
                    if ref_name in self.schema_resolver._schema_registry:
                        resolved_name = self.schema_resolver.resolve_schema_name(
                            ref_name,
                            zone,
                        )
                        types.append(Variable(value=resolved_name))
                    else:
                        # Fallback для незарегистрированных схем
                        types.append(Variable(value="dict"))
                elif variant.get("type") == "object" and "title" in variant:
                    # Inline объект с title
                    title = variant["title"]
                    resolved_name = self.schema_resolver.resolve_schema_name(
                        title,
                        zone,
                    )
                    types.append(Variable(value=resolved_name))
                else:
                    types.append(self._get_type(variant, zone))

            if len(types) == 1:
                result = types[0]
            else:
                result = Variable(value=types, wrap_name="Union")

            if has_null:
                result = Variable(value=result, wrap_name="Optional")

            return result

        # Базовый тип
        return Variable(value=type_mapping.get(schema_type, "str"))

    def _get_type_for_model_field(self, schema: Dict, zone: str) -> Variable:
        """Получение типа для поля модели с правильными $ref"""
        if not schema:
            return Variable(value="Any")

        # anyOf/oneOf в поле модели
        if schema.get("anyOf") or schema.get("oneOf"):
            variants = schema.get("anyOf", []) + schema.get("oneOf", [])
            types = []
            has_null = False

            for variant in variants:
                if variant.get("type") == "null":
                    has_null = True
                elif "$ref" in variant:
                    ref_name = variant["$ref"].replace("#/components/schemas/", "")
                    # Проверяем что схема зарегистрирована
                    if ref_name in self.schema_resolver._schema_registry:
                        schema_zone = self.schema_resolver.get_schema_zone(ref_name)
                        resolved_name = self.schema_resolver.resolve_schema_name(
                            ref_name, zone
                        )

                        # Используем модель с правильным именем
                        types.append(Variable(value=f'"{resolved_name}"'))
                    else:
                        # Fallback для незарегистрированных схем
                        types.append(Variable(value="dict"))
                elif variant.get("type") == "object" and "title" in variant:
                    # Inline объект с title - ищем зарегистрированную схему
                    title = variant["title"]
                    resolved_name = self.schema_resolver.resolve_schema_name(
                        title,
                        zone,
                    )
                    types.append(Variable(value=f'"{resolved_name}"'))
                elif variant.get("type") == "array" and "items" in variant:
                    items = variant["items"]
                    if "$ref" in items:
                        ref_name = items["$ref"].replace("#/components/schemas/", "")
                        resolved_name = self.schema_resolver.resolve_schema_name(
                            ref_name, zone
                        )
                        types.append(
                            Variable(value=f'"{resolved_name}"', wrap_name="List")
                        )
                    elif items.get("type") == "object" and "title" in items:
                        # Inline объект с title - используем fallback логику
                        title = items["title"]
                        resolved_name = self.schema_resolver.resolve_schema_name(
                            title,
                            zone,
                        )
                        types.append(
                            Variable(value=f'"{resolved_name}"', wrap_name="List")
                        )
                    else:
                        item_type = self._get_type_for_model_field(items, zone)
                        if str(item_type) != "Any":  # Избегаем List[Any] если можем
                            types.append(Variable(value=item_type, wrap_name="List"))
                        else:
                            types.append(Variable(value="list"))
                else:
                    types.append(self._get_type_for_model_field(variant, zone))

            if len(types) == 1:
                result = types[0]
            else:
                result = Variable(value=types, wrap_name="Union")

            if has_null:
                result = Variable(value=result, wrap_name="Optional")

            return result

        # Прямой $ref
        if "$ref" in schema:
            ref_name = schema["$ref"].replace("#/components/schemas/", "")

            # Проверяем что схема зарегистрирована
            if ref_name in self.schema_resolver._schema_registry:
                schema_zone = self.schema_resolver.get_schema_zone(ref_name)
                resolved_name = self.schema_resolver.resolve_schema_name(ref_name, zone)

                # Используем модель с правильным именем
                return Variable(value=f'"{resolved_name}"')
            else:
                # Fallback для незарегистрированных схем
                return Variable(value="dict")

        # Array с $ref элементами
        if schema.get("type") == "array" and "items" in schema:
            items = schema["items"]
            if "$ref" in items:
                ref_name = items["$ref"].replace("#/components/schemas/", "")
                resolved_name = self.schema_resolver.resolve_schema_name(
                    ref_name,
                    zone,
                )
                return Variable(value=f'"{resolved_name}"', wrap_name="List")
            elif items.get("type") == "object" and "title" in items:
                # Inline объект с title - используем fallback логику
                title = items["title"]
                resolved_name = self.schema_resolver.resolve_schema_name(
                    title,
                    zone,
                )
                return Variable(value=f'"{resolved_name}"', wrap_name="List")
            else:
                item_type = self._get_type_for_model_field(items, zone)
                return Variable(value=item_type, wrap_name="List")

        # Inline object с title (развернутая схема)
        if schema.get("type") == "object" and "title" in schema:
            title = schema["title"]
            resolved_name = self.schema_resolver.resolve_schema_name(
                title,
                zone,
            )
            return Variable(value=f'"{resolved_name}"')

        # Fallback к обычному типу
        return self._get_type(schema, zone)

    def _get_type_for_endpoint_parameter(self, schema: Dict) -> Variable:
        """Получение типа для endpoint параметра с полной поддержкой моделей"""
        if not schema:
            return Variable(value="Any")

        # anyOf/oneOf в параметре endpoint
        if schema.get("anyOf") or schema.get("oneOf"):
            variants = schema.get("anyOf", []) + schema.get("oneOf", [])
            types = []
            has_null = False

            for variant in variants:
                if variant.get("type") == "null":
                    has_null = True
                elif "$ref" in variant:
                    ref_name = variant["$ref"].replace("#/components/schemas/", "")
                    # Используем прямую очистку имени - реестр может быть не заполнен
                    clean_name = self._get_clean_schema_name(ref_name)
                    types.append(Variable(value=f'"{clean_name}"'))
                else:
                    types.append(self._get_type_for_endpoint_parameter(variant))

            if len(types) == 1:
                result = types[0]
            else:
                result = Variable(value=types, wrap_name="Union")

            if has_null:
                result = Variable(value=result, wrap_name="Optional")

            return result

        # Прямой $ref
        if "$ref" in schema:
            ref_name = schema["$ref"].replace("#/components/schemas/", "")
            # Используем прямую очистку имени - реестр может быть не заполнен
            clean_name = self._get_clean_schema_name(ref_name)
            return Variable(value=f'"{clean_name}"')

        # Array с элементами
        if schema.get("type") == "array" and "items" in schema:
            items = schema["items"]
            if "$ref" in items:
                ref_name = items["$ref"].replace("#/components/schemas/", "")
                # Используем прямую очистку имени - реестр может быть не заполнен
                clean_name = self._get_clean_schema_name(ref_name)
                return Variable(value=f'"{clean_name}"', wrap_name="List")
            else:
                item_type = self._get_type_for_endpoint_parameter(items)
                return Variable(value=item_type, wrap_name="List")

                # Fallback к обычному типу - используем базовые типы
        schema_type = schema.get("type", "string") 
        type_mapping = {
            "string": "str",
            "integer": "int", 
            "boolean": "bool",
            "number": "float",
            "object": "dict",
            "array": "list",
        }
        return Variable(value=type_mapping.get(schema_type, "str"))

    def _add_helper_methods(self, zone_class):
        """Добавление хелпер методов в zone класс для чистоты endpoints"""
        
        # _prepare_params helper
        zone_class.add_function(
            "_prepare_params",
            parameters=[
                Parameter(name="self"),
                Parameter(name="locals_dict", var_type=Variable(value="dict")),
            ],
            code=CodeBlock(
                code="return {k[:-6]: v for k, v in locals_dict.items() if k.endswith('_query') and not models.is_not_set(v)} or None"
            ),
        )
        
        # _prepare_body_data helper  
        zone_class.add_function(
            "_prepare_body_data", 
            parameters=[
                Parameter(name="self"),
                Parameter(name="locals_dict", var_type=Variable(value="dict")),
            ],
            code=CodeBlock(
                code="""body_data = {}
for k, v in locals_dict.items():
    if k.endswith('_body') and not models.is_not_set(v):
        if hasattr(v, 'model_dump'):
            body_data[k[:-5]] = v.model_dump()
        elif isinstance(v, list) and v and hasattr(v[0], 'model_dump'):
            body_data[k[:-5]] = [item.model_dump() for item in v]
        else:
            body_data[k[:-5]] = v
return body_data if body_data else None"""
            ),
        )
        
        # _prepare_files helper
        zone_class.add_function(
            "_prepare_files",
            parameters=[
                Parameter(name="self"),
                Parameter(name="locals_dict", var_type=Variable(value="dict")),
            ], 
            code=CodeBlock(
                code="return {k[:-5]: v for k, v in locals_dict.items() if k.endswith('_file') and not models.is_not_set(v)} or None"
            ),
        )
        
        # _handle_request helper с обработкой response
        response_handling = self._generate_response_handling_code()
        zone_class.add_function(
            "_handle_request",
            parameters=[
                Parameter(name="self"), 
                Parameter(name="method", var_type=Variable(value="str")),
                Parameter(name="path", var_type=Variable(value="str")),
                Parameter(name="params", var_type=Variable(value="Optional[dict]")),
                Parameter(name="data", var_type=Variable(value="Optional[dict]")),
                Parameter(name="files", var_type=Variable(value="Optional[dict]")),
            ],
            async_def=True,
            response="Any",
            code=CodeBlock(
                code=f"""response = await self.client._send_request(
    method=method,
    path=path, 
    params=params,
    data=data,
    files=files
)

{response_handling}"""
            ),
        )

    def _generate_response_handling_code(self) -> str:
        """Генерация кода обработки response для хелпер метода"""
        return """if not hasattr(response, 'status_code'):
    return response

data = await response.json()
return data"""

    def _add_cross_zone_imports(self, file: CodeFile, current_zone: str):
        """Добавление кросс-зонных импортов для endpoints"""
        cross_imports = set()

        # Собираем все зоны которые используются в этой зоне
        for schema_name, info in self.schema_resolver._schema_registry.items():
            schema_zone = info["zone"]
            if schema_zone != current_zone and schema_zone != "common":
                cross_imports.add(schema_zone)

        # Добавляем импорты
        for zone in sorted(cross_imports):
            file.imports.append(f"from ..models import {zone}")

    def _add_model_cross_imports(self, models_file: CodeFile, current_zone: str):
        """Добавление кросс-импортов между моделями разных зон"""
        cross_zones = set()

        # Собираем все зоны которые могут быть ссылками в этой зоне
        for schema_name, info in self.schema_resolver._schema_registry.items():
            schema_zone = info["zone"]
            if schema_zone != current_zone and schema_zone != "common":
                cross_zones.add(schema_zone)

        # Добавляем TYPE_CHECKING блок для кросс-зонных ссылок
        if cross_zones:
            models_file.imports.append("")
            models_file.imports.append("if TYPE_CHECKING:")

            for zone in sorted(cross_zones):
                models_file.imports.append(f"    from . import {zone}")

    def _add_model_rebuilds(self):
        """Добавление model_rebuild() для всех моделей с forward references"""
        # Добавляем model_rebuild() в конце каждого файла моделей
        for file in self.project.files:
            if file.file_name.startswith("models/") and file.file_name.endswith(".py"):
                if file.classes:
                    model_names = list(file.classes.keys())
                    print(f"DEBUG: File {file.file_name} has models: {model_names}")

                    rebuild_code = []
                    rebuild_code.append("")
                    rebuild_code.append("# Model rebuilds for forward references")
                    for model_name in sorted(model_names):
                        rebuild_code.append(f"{model_name}.model_rebuild()")

                    file.add_code_block(
                        CodeBlock(
                            code="\n".join(rebuild_code), order=-1000
                        )  # Добавляем в конец
                    )

    def _add_model_rebuilds_direct(self):
        """Прямое добавление model_rebuild() в файлы"""
        for file in self.project.files:
            if file.file_name.startswith("models/") and file.file_name.endswith(".py"):
                if file.classes:
                    model_names = sorted(file.classes.keys())

                    # Добавляем в конец файла через CodeBlock
                    rebuild_code = ["", "# Model rebuilds for forward references"]
                    for model_name in model_names:
                        rebuild_code.append(f"{model_name}.model_rebuild()")

                    file.add_code_block(
                        CodeBlock(code="\n".join(rebuild_code), order=-100)
                    )

    def _add_model_rebuilds_final(self):
        """Добавление model_rebuild() в конце файлов после всех моделей"""
        for file in self.project.files:
            if file.file_name.startswith("models/") and file.file_name.endswith(".py"):
                if file.classes:
                    model_names = sorted(file.classes.keys())

                    # Добавляем как код блок
                    rebuild_code = [""]
                    rebuild_code.append("# Model rebuilds for forward references")
                    for model_name in model_names:
                        rebuild_code.append(f"{model_name}.model_rebuild()")

                    file.add_code_block(
                        CodeBlock(code="\n".join(rebuild_code), order=-1)
                    )
