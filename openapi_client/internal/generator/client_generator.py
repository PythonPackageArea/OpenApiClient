import re
from typing import Dict, Any, List, Optional, Set, Tuple
from collections import defaultdict

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

# from .http_client import aiohttp_common - moved to templates


class ClientGenerator:
    """Генератор API клиента из OpenAPI"""

    def __init__(
        self,
        openapi_dict: Dict[str, Any],
        source_url: str = None,
        original_spec: Dict[str, Any] = None,
    ):
        self.openapi_dict = openapi_dict
        self.original_spec = (
            original_spec or openapi_dict
        )  # Используем оригинальную спецификацию если передана
        self.source_url = source_url
        self.project = Project(name="api")
        self.schema_resolver = SchemaNameResolver()
        self.zones = {}  # zone_name -> {endpoints_file, endpoints_class}
        self.used_schemas = set()  # Только используемые схемы
        self.schema_file_names = {}  # schema_name -> file_name mapping

    def _analyze_schema_names(self) -> Dict[str, str]:
        """Анализ имен схем для генерации оптимальных имен файлов"""
        schemas = self.openapi_dict.get("components", {}).get("schemas", {})
        schema_to_filename = {}

        for schema_name in schemas.keys():
            # Получаем чистое имя схемы
            clean_name = self._get_clean_schema_name(schema_name)

            # Генерируем имя файла из полного имени модели
            filename = self._snake_case(clean_name)
            schema_to_filename[schema_name] = filename

        return schema_to_filename

    def generate(self) -> Project:
        """Основная генерация"""
        self._create_base_files()
        self.schema_file_names = self._analyze_schema_names()  # Анализируем имена схем
        self._register_all_schemas()  # ОТКАТ: регистрируем ВСЕ схемы
        self._generate_schemas()
        self._generate_endpoints()
        self._add_zone_model_references()  # Добавляем ссылки на модели в endpoint классы
        self._finalize_structure()
        return self.project

    def _register_all_schemas(self):
        """Регистрация всех схем для правильного разрешения имен"""
        schemas = self.openapi_dict.get("components", {}).get("schemas", {})

        # Регистрируем основные схемы
        for schema_name, schema_spec in schemas.items():
            zone = "common"  # Все модели теперь в общей зоне
            clean_name = self._get_clean_schema_name(schema_name)
            self.schema_resolver.register_schema(schema_name, clean_name, zone)

        # Регистрируем inline схемы с title из responses
        for path, path_spec in self.openapi_dict.get("paths", {}).items():
            for method, method_spec in path_spec.items():
                for status_code, response_spec in method_spec.get(
                    "responses", {}
                ).items():
                    if status_code.startswith("2"):  # Только успешные ответы
                        content = response_spec.get("content", {})
                        for content_type, content_spec in content.items():
                            schema = content_spec.get("schema", {})
                            if schema.get("title") and not "$ref" in schema:
                                # Это inline схема с title - регистрируем её
                                title = schema["title"]
                                zone = "common"  # Все модели в общей зоне
                                clean_name = self._get_clean_schema_name(title)
                                self.schema_resolver.register_schema(
                                    title, clean_name, zone
                                )

    def _create_base_files(self):
        """Создание базовых файлов проекта"""
        # Основные файлы
        self.project.add_file("common.py").add_code_block(
            CodeBlock(code=templates.aiohttp_common)
        )
        self.project.add_file("client.py").add_code_block(
            CodeBlock(code=templates.client)
        )
        self.project.add_file("constants.py").add_code_block(
            CodeBlock(code=templates.models)
        )
        self.project.add_file("utils.py").add_code_block(
            CodeBlock(code=templates.utils)
        )
        self.project.add_file("decorators.py").add_code_block(
            CodeBlock(code=templates.decorators)
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
        """Генерация всех Pydantic моделей из components/schemas в отдельные файлы"""
        schemas = self.openapi_dict.get("components", {}).get("schemas", {})

        # Создаем папку models и __init__.py
        models_init = self.project.add_file("models/__init__.py")
        models_init.imports.extend(
            [
                "# Auto-generated models",
                "from typing import TYPE_CHECKING",
                "",
                "# Import all models for easy access",
            ]
        )

        all_models = []
        models_needing_rebuild = []

        # Генерируем отдельный файл для каждой схемы
        for schema_name, schema_spec in schemas.items():
            clean_name = self._get_clean_schema_name(schema_name)
            filename = self.schema_file_names.get(
                schema_name, self._snake_case(clean_name)
            )

            # Генерируем модель в отдельном файле
            needs_rebuild = self._generate_model(
                schema_name, clean_name, schema_spec, filename
            )
            if needs_rebuild:
                models_needing_rebuild.append(clean_name)

            all_models.append((filename, clean_name))

        # Добавляем импорты всех моделей в __init__.py
        # Используем set для удаления дубликатов импортов
        unique_imports = set()
        for filename, model_name in all_models:
            unique_imports.add(f"from .{filename} import {model_name}")

        models_init.imports.extend(sorted(unique_imports))

        # Экспортируем все модели через __all__
        # Собираем уникальные имена моделей
        unique_model_names = sorted(set(model_name for _, model_name in all_models))
        models_init.add_code_block(CodeBlock(code=f"\n__all__ = {unique_model_names}"))

        # Добавляем model_rebuild() для моделей с TYPE_CHECKING импортами
        if models_needing_rebuild:
            rebuild_code = "\n# Rebuild models with forward references to resolve TYPE_CHECKING imports"
            for model_name in models_needing_rebuild:
                rebuild_code += f"\n{model_name}.model_rebuild()"
            models_init.add_code_block(CodeBlock(code=rebuild_code, order=100))

    def _generate_endpoints(self):
        """Генерация endpoints по тегам"""
        for path, path_spec in self.openapi_dict.get("paths", {}).items():
            for method, method_spec in path_spec.items():
                zone = self._get_endpoint_zone(method_spec)
                self._ensure_zone(zone)
                self._generate_endpoint_method(path, method, method_spec, zone)

    def _generate_endpoint_method(self, path: str, method: str, spec: Dict, zone: str):
        """Генерация метода endpoint с декораторами"""
        zone_class = self.zones[zone.lower()]["endpoints_class"]

        # Генерируем имя функции
        func_name = self._generate_function_name(path, method, spec)

        # Параметры
        parameters = [Parameter(name="self")]

        # Найдем все path параметры из URL
        import re

        path_params = re.findall(r"\{(\w+)\}", path)

        # Используем только параметры из OpenAPI спецификации
        for param_spec in spec.get("parameters", []):
            param = self._create_parameter(param_spec, path, path_params)
            parameters.append(param)

        # Body параметры
        request_body = spec.get("requestBody", {})
        if request_body:
            body_params = self._create_body_parameters(request_body, zone)
            parameters.extend(body_params)

        # Тип возврата
        return_type = self._get_return_type(spec.get("responses", {}), zone)

        # Получаем чистое имя модели для декоратора
        clean_model_type = self._get_clean_model_type(spec.get("responses", {}), zone)

        # Если return_type = "Any", но у нас есть конкретная модель, используем её
        if return_type == "Any" and clean_model_type != "Any":
            return_type = clean_model_type

        # Создаем декоратор
        if clean_model_type != "Any":
            decorator = f"@{method}('{path}', response_model={clean_model_type})"
        else:
            decorator = f"@{method}('{path}')"

        # Создаем функцию с декоратором
        func = zone_class.add_function(
            func_name,
            parameters=parameters,
            async_def=True,
            response=return_type,
            description=spec.get("description", ""),
            decorators=[decorator],
        )

        # Декораторы делают всю работу - пустое тело
        func.code = CodeBlock(code="pass")

    def _add_zone_model_references(self):
        """Добавляет ссылки на все связанные модели в каждый endpoint класс"""
        for zone_name, zone_info in self.zones.items():
            zone_class = zone_info["endpoints_class"]

            # Собираем все модели используемые в этой зоне
            zone_models = self._collect_zone_models(zone_name)

            # Добавляем class variables для каждой модели
            for model_name in sorted(zone_models):
                var_name = self._snake_case(model_name)
                zone_class.parameters.append(
                    Parameter(
                        name=var_name,
                        default=Variable(value=model_name),
                        var_type=None,  # Без типа для class variable
                    )
                )

    def _collect_zone_models(self, zone_name: str) -> set:
        """Собирает только существующие модели связанные с зоной"""
        zone_models = set()
        zone_info = self.zones[zone_name]
        zone_class = zone_info["endpoints_class"]

        # Получаем список всех существующих моделей
        existing_models = self._get_all_existing_models()

        # Проходим по всем методам зоны
        for func in zone_class.functions.values():
            # Ищем response_model в декораторах
            for decorator in func.decorators:
                if "response_model=" in decorator:
                    # Извлекаем имя модели из декоратора
                    import re

                    match = re.search(r"response_model=(\w+)", decorator)
                    if match:
                        model_name = match.group(1)
                        # Добавляем только если модель существует
                        if model_name in existing_models:
                            zone_models.add(model_name)

            # Ищем модели в типах параметров (для enum'ов и других типов)
            for param in func.parameters:
                if param.var_type and param.var_type.value:
                    # Извлекаем имя типа (может быть Optional[ModelName] или ModelName)
                    import re

                    # Ищем имена моделей в типах (включая Optional, List, etc.)
                    type_matches = re.findall(r"([A-Z]\w+)", str(param.var_type.value))
                    for type_name in type_matches:
                        if type_name in existing_models:
                            zone_models.add(type_name)

        return zone_models

    def _get_all_existing_models(self) -> set:
        """Получает список всех существующих моделей в проекте"""
        existing_models = set()

        # Проходим по всем model файлам
        for file in self.project.files:
            if (
                file.file_name.startswith("models/")
                and file.file_name != "models/__init__.py"
            ):
                # Добавляем имена классов из файла
                for class_name in file.classes.keys():
                    existing_models.add(class_name)

        return existing_models

    def _create_parameter(
        self, param_spec: Dict, path_str: str = "", path_params: List[str] = None
    ) -> Parameter:
        """Создание параметра с правильным именованием"""
        name = param_spec["name"]
        param_type = param_spec["in"]
        path_params = path_params or []

        # Проверяем, является ли этот параметр path параметром
        is_path_param = False

        if param_type == "path":
            is_path_param = True
        elif f"{{{name}}}" in path_str:
            # Точное совпадение имени параметра с placeholder в пути
            is_path_param = True
        # Убираем автоматическое превращение query в path - это было неправильно

        if is_path_param:
            param_name = f"{name}_path"
        elif param_type == "query":
            param_name = f"{name}_query"
        else:
            param_name = name

        var_type = self._get_type(param_spec.get("schema", {}), "")

        default = None
        if not param_spec.get("required", False):
            default = Variable(value="NOTSET")

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
                # Для body параметров используем правильное разрешение с учетом зоны
                resolved_name = self.schema_resolver.resolve_schema_name(ref_name, zone)
                param_name = "request_body"
                var_type = Variable(value=f'"{resolved_name}"')
                default = Variable(value="NOTSET")

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

                    # Для body параметров используем правильное разрешение типов с зоной
                    var_type = self._get_type_for_model_field(prop_spec, zone)
                    default = Variable(value="NOTSET")

                    parameters.append(
                        Parameter(name=param_name, var_type=var_type, default=default)
                    )

        return parameters

    def _find_existing_enum(self, enum_values: List, zone: str) -> Optional[str]:
        """Поиск существующего enum с такими же значениями"""
        enum_values_set = set(enum_values)

        # Сначала ищем в зарегистрированных схемах
        schemas = self.openapi_dict.get("components", {}).get("schemas", {})
        for schema_name, schema_spec in schemas.items():
            if schema_spec.get("enum") and set(schema_spec["enum"]) == enum_values_set:
                # Найдена схема с такими же enum значениями
                if schema_name in self.schema_resolver._schema_registry:
                    info = self.schema_resolver._schema_registry[schema_name]
                    clean_name = info["clean_name"]
                    schema_zone = info["zone"]

                    # Если это та же зона - возвращаем имя без префикса
                    if schema_zone == zone:
                        return clean_name
                    # Если другая зона - возвращаем с префиксом
                    elif schema_zone != "common":
                        return f"{schema_zone}.{clean_name}"
                    else:
                        return clean_name

        return None

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
            enum_values = schema["enum"]
            # Ищем существующий enum с теми же значениями
            existing_enum = self._find_existing_enum(enum_values, zone)
            if existing_enum:
                return Variable(value=existing_enum)
            else:
                # Fallback к Literal если enum не найден
                enum_values_repr = [repr(v) for v in enum_values]
                return Variable(value=enum_values_repr, wrap_name="Literal")

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
                                    clean_name = self._get_clean_schema_name(ref_name)
                                    type_variants.append(clean_name)
                                elif variant.get("type") == "null":
                                    has_null = True
                                elif (
                                    variant.get("type") == "object"
                                    and "title" in variant
                                ):
                                    # Это развернутая схема с title - ищем зарегистрированную схему
                                    title = variant["title"]
                                    # Ищем схему с таким title в правильной зоне
                                    found = False
                                    for schema_name, schema_spec in (
                                        self.openapi_dict.get("components", {})
                                        .get("schemas", {})
                                        .items()
                                    ):
                                        if schema_spec.get("title") == title:
                                            schema_clean_name = (
                                                self._get_clean_schema_name(schema_name)
                                            )
                                            # Проверяем зону - очень гибкий поиск
                                            if zone:
                                                zone_lower = zone.lower()
                                                schema_lower = schema_clean_name.lower()
                                                title_lower = title.lower()

                                                # Ищем модель содержащую зону (или её часть) и title
                                                zone_match = (
                                                    zone_lower in schema_lower
                                                    or any(
                                                        part in schema_lower
                                                        for part in zone_lower.split(
                                                            "_"
                                                        )
                                                        if len(part) > 2
                                                    )
                                                )
                                                title_match = (
                                                    title_lower in schema_lower
                                                )

                                                if zone_match and title_match:
                                                    type_variants.append(
                                                        schema_clean_name
                                                    )
                                                    found = True
                                                    break
                                            else:
                                                type_variants.append(schema_clean_name)
                                            found = True
                                            break
                                    if not found:
                                        clean_name = self._get_clean_schema_name(title)
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
                            clean_name = self._get_clean_schema_name(ref_name)
                            success_responses.append(clean_name)
                        elif schema.get("type") == "array" and "items" in schema:
                            # Массив моделей
                            items = schema["items"]
                            if "$ref" in items:
                                ref_name = items["$ref"].replace(
                                    "#/components/schemas/", ""
                                )
                                clean_name = self._get_clean_schema_name(ref_name)
                                success_responses.append(f"List[{clean_name}]")
                            else:
                                var_type = self._get_type(schema, zone)
                                success_responses.append(str(var_type))
                        elif schema.get("type") == "object" and "title" in schema:
                            # Проверяем additionalProperties - это должно быть Dict, а не модель
                            if "additionalProperties" in schema:
                                additional_props = schema["additionalProperties"]
                                value_type = self._get_type(additional_props, zone)
                                success_responses.append(f"Dict[str, {value_type}]")
                            else:
                                # Инлайн объект с title - используем зарегистрированную схему
                                title = schema["title"]
                                found_schema = False
                                # Ищем схему с таким title в текущей зоне
                                for schema_name, schema_spec in (
                                    self.openapi_dict.get("components", {})
                                    .get("schemas", {})
                                    .items()
                                ):
                                    if schema_spec.get("title") == title:
                                        schema_clean_name = self._get_clean_schema_name(
                                            schema_name
                                        )
                                        # Проверяем зону - очень гибкий поиск
                                        if zone:
                                            zone_lower = zone.lower()
                                            schema_lower = schema_clean_name.lower()
                                            title_lower = title.lower()

                                            # Ищем модель содержащую зону (или её часть) и title
                                            zone_match = (
                                                zone_lower in schema_lower
                                                or any(
                                                    part in schema_lower
                                                    for part in zone_lower.split("_")
                                                    if len(part) > 2
                                                )
                                            )
                                            title_match = title_lower in schema_lower

                                            if zone_match and title_match:
                                                success_responses.append(
                                                    schema_clean_name
                                                )
                                                found_schema = True
                                                break
                                        else:
                                            # Если нет зоны, берем первую найденную
                                            success_responses.append(schema_clean_name)
                                            found_schema = True
                                            break

                                if not found_schema:
                                    # Fallback - используем title как есть
                                    clean_name = self._get_clean_schema_name(title)
                                    success_responses.append(clean_name)
                        else:
                            var_type = self._get_type(schema, zone)
                            success_responses.append(str(var_type))

        # Убираем дубликаты, сохраняя порядок
        unique_responses = []
        for response in success_responses:
            if response not in unique_responses:
                unique_responses.append(response)

        if len(unique_responses) == 1:
            return unique_responses[0]
        elif len(unique_responses) > 1:
            return f"Union[{', '.join(unique_responses)}]"
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

    def _get_endpoint_zone(self, method_spec: Dict) -> str:
        """Получение зоны для endpoint"""
        tags = method_spec.get("tags", [])
        if tags:
            tag = tags[0]
            # Исправления для зон с несоответствием названий
            if tag == "support":
                return "support_messages"
            return self._snake_case(tag)
        return "default"

    def _ensure_zone(self, zone: str):
        """Создание файлов зоны если нужно"""
        # Нормализуем имя зоны к lowercase для консистентности файлов
        zone_key = zone.lower()

        if zone_key not in self.zones:
            # endpoints/<zone>.py (всегда lowercase для консистентности)
            endpoints_file = self.project.add_file(f"endpoints/{zone.lower()}.py")
            endpoints_file.imports.extend(
                [
                    "from ..decorators import get, post, put, delete, patch",
                    "from ..common import AiohttpClient",
                    "from typing import Optional, List, Any, Union, Literal, Dict",
                    "from datetime import datetime",
                    "from ..constants import NOTSET",
                    "from ..models import *",
                ]
            )

            # Кросс-импорты уже добавлены выше

            # Используем ту же логику очистки имен что и для схем
            zone_class_name = self.schema_resolver._clean_schema_name(zone)
            zone_class = endpoints_file.add_class(zone_class_name)

            zone_class.add_function(
                "__init__",
                parameters=[
                    Parameter(name="self"),
                    Parameter(name="client", var_type=Variable(value="AiohttpClient")),
                ],
                code=CodeBlock(code="self.client = client"),
            )

            self.zones[zone_key] = {
                "endpoints_file": endpoints_file,
                "endpoints_class": zone_class,
            }

    def _collect_field_dependencies(self, field_spec: Dict, dependencies: Set[str]):
        """Рекурсивно собирает зависимости из спецификации поля"""
        if "$ref" in field_spec:
            ref_name = field_spec["$ref"].replace("#/components/schemas/", "")
            dependencies.add(ref_name)
        elif field_spec.get("anyOf") or field_spec.get("oneOf"):
            variants = field_spec.get("anyOf", []) + field_spec.get("oneOf", [])
            for variant in variants:
                self._collect_field_dependencies(variant, dependencies)
        elif field_spec.get("type") == "array" and "items" in field_spec:
            self._collect_field_dependencies(field_spec["items"], dependencies)
        elif field_spec.get("type") == "object" and "title" in field_spec:
            # Inline объект - пытаемся найти соответствующую схему
            title = field_spec["title"]
            for reg_name, info in self.schema_resolver._schema_registry.items():
                schemas_dict = self.original_spec.get("components", {}).get(
                    "schemas", {}
                )
                if reg_name in schemas_dict:
                    reg_schema = schemas_dict[reg_name]
                    if reg_schema.get("title") == title:
                        dependencies.add(reg_name)
                        break

    def _add_model_to_file(
        self,
        model_file: CodeFile,
        original_name: str,
        clean_name: str,
        schema_spec: Dict,
        dependencies: Set[str],
    ):
        """Добавление модели к файлу"""
        if schema_spec.get("enum"):
            # Enum модель
            model_class = model_file.add_class(clean_name, inherits=["str", "Enum"])
            for enum_value in schema_spec["enum"]:
                model_class.parameters.append(
                    Parameter(
                        name=str(enum_value).upper(),
                        default=Variable(value=repr(enum_value)),
                    )
                )
        elif (
            schema_spec.get("type") == "object"
            and "additionalProperties" in schema_spec
            and not schema_spec.get("properties")
        ):
            # Схема с additionalProperties без properties - это должен быть Dict, а не модель
            # Пропускаем создание модели, она будет обрабатываться как Dict[str, type]
            return
        else:
            # Обычная модель
            model_class = model_file.add_class(clean_name, inherits=["BaseModel"])

            properties = schema_spec.get("properties", {})
            required = schema_spec.get("required", [])

            # Пытаемся получить оригинальные свойства из original_spec
            original_properties = {}
            if original_name in self.original_spec.get("components", {}).get(
                "schemas", {}
            ):
                original_properties = self.original_spec["components"]["schemas"][
                    original_name
                ].get("properties", {})

            for field_name, field_spec in properties.items():
                # Если есть оригинальная спецификация поля, используем ее для определения типа
                original_field_spec = original_properties.get(field_name, field_spec)

                field_type = self._get_type_for_model_field(
                    original_field_spec, "", dependencies
                )

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

    def _generate_model(
        self, original_name: str, clean_name: str, schema_spec: Dict, filename: str
    ) -> bool:
        """Генерация Pydantic модели в отдельный файл"""
        # Создаем отдельный файл для каждой модели
        model_file = self.project.add_file(f"models/{filename}.py")

        # Базовые импорты
        model_file.imports.extend(
            [
                "from __future__ import annotations",
                "",
                "from pydantic import BaseModel",
                "from enum import Enum",
                "from typing import Optional, Union, List, Dict, Literal, Any, TYPE_CHECKING",
                "from datetime import datetime",
            ]
        )

        if schema_spec.get("enum"):
            # Enum модель
            model_class = model_file.add_class(clean_name, inherits=["str", "Enum"])
            for enum_value in schema_spec["enum"]:
                model_class.parameters.append(
                    Parameter(
                        name=str(enum_value).upper(),
                        default=Variable(value=repr(enum_value)),
                    )
                )
        elif (
            schema_spec.get("type") == "object"
            and "additionalProperties" in schema_spec
            and not schema_spec.get("properties")
        ):
            # Схема с additionalProperties без properties - это должен быть Dict, а не модель
            # Пропускаем создание модели, она будет обрабатываться как Dict[str, type]
            return
        else:
            # Обычная модель
            model_class = model_file.add_class(clean_name, inherits=["BaseModel"])

            properties = schema_spec.get("properties", {})
            required = schema_spec.get("required", [])

            # Собираем зависимости для импортов
            dependencies = set()

            # Пытаемся получить оригинальные свойства из original_spec
            original_properties = {}
            if original_name in self.original_spec.get("components", {}).get(
                "schemas", {}
            ):
                original_properties = self.original_spec["components"]["schemas"][
                    original_name
                ].get("properties", {})

            for field_name, field_spec in properties.items():
                # Если есть оригинальная спецификация поля, используем ее для определения типа
                original_field_spec = original_properties.get(field_name, field_spec)

                field_type = self._get_type_for_model_field(
                    original_field_spec, "", dependencies
                )

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

            # Добавляем импорты зависимостей под TYPE_CHECKING
            type_checking_imports = []
            for dep in sorted(dependencies):
                if dep != clean_name:  # Не импортируем сам себя
                    dep_filename = self.schema_file_names.get(
                        dep, self._snake_case(dep)
                    )
                    dep_clean_name = self._get_clean_schema_name(dep)
                    type_checking_imports.append(
                        f"    from .{dep_filename} import {dep_clean_name}"
                    )

            if type_checking_imports:
                model_file.imports.append("")
                model_file.imports.append("if TYPE_CHECKING:")
                model_file.imports.extend(type_checking_imports)

        # Добавляем метод rebuild в конец файла только для BaseModel (не для Enum)
        # и только если нет TYPE_CHECKING импортов
        needs_rebuild_in_init = False
        if not schema_spec.get("enum"):
            if not type_checking_imports:
                # Нет TYPE_CHECKING импортов - добавляем model_rebuild() в файл
                model_file.add_code_block(
                    CodeBlock(
                        code=f"\n# Rebuild model to resolve forward references\n{clean_name}.model_rebuild()",
                        order=-100,  # Отрицательный order чтобы был в самом конце
                    )
                )
            else:
                # Есть TYPE_CHECKING импорты - нужен model_rebuild() в __init__.py
                needs_rebuild_in_init = True

        return needs_rebuild_in_init

    def _get_clean_schema_name(self, schema_name: str) -> str:
        """Получение чистого имени схемы"""
        return self.schema_resolver._clean_schema_name(schema_name)

    def _finalize_structure(self):
        """Финализация структуры проекта"""
        # Убираем пустые зоны (без endpoints)
        self._remove_empty_zones()

        # Создаем динамический client.py с прямым доступом к зонам
        self._generate_dynamic_client()

    def _remove_empty_zones(self):
        """Удаление зон без endpoint методов"""
        empty_zones = []

        for zone_name, zone_info in self.zones.items():
            zone_class = zone_info["endpoints_class"]
            # Проверяем есть ли методы кроме __init__
            has_methods = any(
                func_name != "__init__" for func_name in zone_class.functions.keys()
            )

            # Удаляем зону если нет методов
            if not has_methods:
                empty_zones.append(zone_name)

        # Удаляем пустые зоны
        for zone_name in empty_zones:
            # Удаляем из проекта
            zone_info = self.zones[zone_name]
            endpoints_file = zone_info["endpoints_file"]

            # Удаляем файл из проекта
            if endpoints_file.file_name in [f.file_name for f in self.project.files]:
                self.project.files = [
                    f
                    for f in self.project.files
                    if f.file_name != endpoints_file.file_name
                ]

            # Удаляем из zones
            del self.zones[zone_name]

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
            zone_imports.append(
                f"    from .endpoints.{zone_name.lower()} import {zone_class}"
            )

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
                        f"from .endpoints.{zone_name.lower()} import {zone_class}"
                    )
                break

    @staticmethod
    def _snake_case(name: str) -> str:
        # Сначала заменяем дефисы на подчеркивания
        name = name.replace("-", "_")

        # Обработка аббревиатур: HTTPValidationError -> http_validation_error
        # Шаг 1: Добавляем подчеркивание перед заглавной буквой, которая следует за строчной
        s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
        # Шаг 2: Добавляем подчеркивание между строчной буквой и заглавной
        s2 = re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1)
        # Шаг 3: Обрабатываем последовательности заглавных букв (HTTP -> HTTP, HTTPError -> HTTP_Error)
        s3 = re.sub("([A-Z]+)([A-Z][a-z])", r"\1_\2", s2)
        # Шаг 4: Убираем дублирующиеся подчеркивания
        s4 = re.sub("_+", "_", s3)
        return s4.lower()

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

            # Универсальная логика: если часть уже в верхнем регистре, оставляем
            if part.isupper() and len(part) <= 4:  # аббревиатуры
                parts.append(part)
            elif part.lower() == "id":
                parts.append("ID")
            else:
                # Обычное PascalCase
                parts.append(part.capitalize())

        return "".join(parts)

    def _get_type(self, schema: Dict, zone: str = "") -> Variable:
        """Получение типа из OpenAPI схемы с правильными $ref"""
        if not schema:
            return Variable(value="Any")

        # $ref ссылки - правильно разрешаем в контексте зоны
        if "$ref" in schema:
            ref_name = schema["$ref"].replace("#/components/schemas/", "")

            # Проверяем исходную схему - если это additionalProperties без properties, то это Dict
            schemas = self.openapi_dict.get("components", {}).get("schemas", {})
            if ref_name in schemas:
                ref_schema = schemas[ref_name]
                if (
                    ref_schema.get("type") == "object"
                    and "additionalProperties" in ref_schema
                    and not ref_schema.get("properties")
                ):
                    # Это Dict, а не модель
                    additional_props = ref_schema["additionalProperties"]
                    value_type = self._get_type(additional_props, zone)
                    return Variable(value=f"str, {value_type}", wrap_name="Dict")

            resolved_name = self.schema_resolver.resolve_schema_name(
                ref_name,
                zone,
            )
            # С from __future__ import annotations кавычки не нужны
            return Variable(value=f'"{resolved_name}"')

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
            enum_values = schema["enum"]
            # Ищем существующий enum с теми же значениями
            existing_enum = self._find_existing_enum(enum_values, zone)
            if existing_enum:
                return Variable(value=existing_enum)
            else:
                # Fallback к Literal если enum не найден
                enum_values_repr = [repr(v) for v in enum_values]
                return Variable(value=enum_values_repr, wrap_name="Literal")

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
                        types.append(Variable(value=f'"{resolved_name}"'))
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
                    types.append(Variable(value=f'"{resolved_name}"'))
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

    def _get_type_for_model_field(
        self, schema: Dict, zone: str, dependencies: Set[str] = None
    ) -> Variable:
        """Получение типа для поля модели с правильными $ref"""
        if not schema:
            return Variable(value="Any")

        # Обработка enum с title (развернутая схема после jsonref)
        if schema.get("enum") and schema.get("title"):
            title = schema["title"]

            # Ищем зарегистрированную схему с таким title
            found_schema = None
            for reg_name, info in self.schema_resolver._schema_registry.items():
                if self._get_clean_schema_name(reg_name) == title:
                    found_schema = reg_name
                    break

            if found_schema:
                if dependencies is not None:
                    dependencies.add(found_schema)
                resolved_name = self.schema_resolver.resolve_schema_name(
                    found_schema, zone, include_zone_prefix=False
                )
                # С from __future__ import annotations кавычки не нужны
                return Variable(value=f'"{resolved_name}"')
            else:
                # Inline enum - создаем Literal вместо dependency
                if schema.get("enum"):
                    enum_values = schema["enum"]
                    literal_values = ", ".join(f"'{v}'" for v in enum_values)
                    return Variable(value=f"Literal[{literal_values}]")
                else:
                    # Обычный title без enum
                    if dependencies is not None:
                        dependencies.add(title)
                    return Variable(value=f'"{title}"')

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
                        if dependencies is not None:
                            dependencies.add(ref_name)
                        resolved_name = self.schema_resolver.resolve_schema_name(
                            ref_name, zone, include_zone_prefix=False
                        )

                        # Используем модель с правильным именем
                        types.append(Variable(value=f'"{resolved_name}"'))
                    else:
                        # Fallback для незарегистрированных схем
                        types.append(Variable(value="dict"))
                elif variant.get("type") == "object" and "title" in variant:
                    # Inline объект с title - ищем зарегистрированную схему
                    title = variant["title"]
                    if dependencies is not None:
                        dependencies.add(title)
                    resolved_name = self.schema_resolver.resolve_schema_name(
                        title, zone, include_zone_prefix=False
                    )
                    types.append(Variable(value=f'"{resolved_name}"'))
                elif variant.get("type") == "array" and "items" in variant:
                    items = variant["items"]
                    if "$ref" in items:
                        ref_name = items["$ref"].replace("#/components/schemas/", "")
                        if dependencies is not None:
                            dependencies.add(ref_name)
                        resolved_name = self.schema_resolver.resolve_schema_name(
                            ref_name, zone, include_zone_prefix=False
                        )
                        types.append(
                            Variable(value=f'"{resolved_name}"', wrap_name="List")
                        )
                    elif items.get("type") == "object" and "title" in items:
                        # Inline объект с title - используем fallback логику
                        title = items["title"]
                        if dependencies is not None:
                            dependencies.add(title)
                        resolved_name = self.schema_resolver.resolve_schema_name(
                            title, zone, include_zone_prefix=False
                        )
                        types.append(
                            Variable(value=f'"{resolved_name}"', wrap_name="List")
                        )
                    else:
                        item_type = self._get_type_for_model_field(
                            items, zone, dependencies
                        )
                        if str(item_type) != "Any":  # Избегаем List[Any] если можем
                            types.append(Variable(value=item_type, wrap_name="List"))
                        else:
                            types.append(Variable(value="list"))
                elif variant.get("enum") and variant.get("title"):
                    # Inline enum в anyOf - создаем Literal напрямую
                    enum_values = variant["enum"]
                    literal_values = ", ".join(f"'{v}'" for v in enum_values)
                    types.append(Variable(value=f"Literal[{literal_values}]"))
                else:
                    types.append(
                        self._get_type_for_model_field(variant, zone, dependencies)
                    )

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
            if dependencies is not None:
                dependencies.add(ref_name)

            # Проверяем что схема зарегистрирована
            if ref_name in self.schema_resolver._schema_registry:
                # Проверяем исходную схему - если это additionalProperties без properties, то это Dict
                schemas = self.openapi_dict.get("components", {}).get("schemas", {})
                if ref_name in schemas:
                    ref_schema = schemas[ref_name]
                    if (
                        ref_schema.get("type") == "object"
                        and "additionalProperties" in ref_schema
                        and not ref_schema.get("properties")
                    ):
                        # Это Dict, а не модель
                        additional_props = ref_schema["additionalProperties"]
                        value_type = self._get_type_for_model_field(
                            additional_props, zone, dependencies
                        )
                        return Variable(value=f"str, {value_type}", wrap_name="Dict")

                resolved_name = self.schema_resolver.resolve_schema_name(
                    ref_name, zone, include_zone_prefix=False
                )

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
                if dependencies is not None:
                    dependencies.add(ref_name)
                resolved_name = self.schema_resolver.resolve_schema_name(
                    ref_name, zone, include_zone_prefix=False
                )
                return Variable(value=f'"{resolved_name}"', wrap_name="List")
            elif items.get("type") == "object" and "title" in items:
                # Inline объект с title - используем fallback логику
                title = items["title"]
                if dependencies is not None:
                    dependencies.add(title)
                resolved_name = self.schema_resolver.resolve_schema_name(
                    title, zone, include_zone_prefix=False
                )
                return Variable(value=f'"{resolved_name}"', wrap_name="List")
            else:
                item_type = self._get_type_for_model_field(items, zone, dependencies)
                return Variable(value=item_type, wrap_name="List")

        # Inline object с title (развернутая схема)
        if schema.get("type") == "object" and "title" in schema:
            # Проверяем additionalProperties - это должно быть Dict, а не модель
            if "additionalProperties" in schema:
                additional_props = schema["additionalProperties"]
                value_type = self._get_type_for_model_field(
                    additional_props, zone, dependencies
                )
                return Variable(value=f"str, {value_type}", wrap_name="Dict")

            title = schema["title"]

            # Ищем зарегистрированную схему с таким title
            # Сравниваем не только title, но и структуру
            found_schema = None
            best_match = None
            best_score = 0

            for reg_name, info in self.schema_resolver._schema_registry.items():
                # Получаем оригинальную схему для сравнения
                schemas_dict = self.openapi_dict.get("components", {}).get(
                    "schemas", {}
                )
                if reg_name in schemas_dict:
                    reg_schema = schemas_dict[reg_name]
                    if reg_schema.get("title") == title:
                        # Сравниваем свойства
                        reg_props = set(reg_schema.get("properties", {}).keys())
                        inline_props = set(schema.get("properties", {}).keys())

                        # Если свойства полностью совпадают - это точное совпадение
                        if reg_props == inline_props:
                            found_schema = reg_name
                            break

                        # Иначе считаем процент совпадения
                        if reg_props and inline_props:
                            common_props = reg_props.intersection(inline_props)
                            score = len(common_props) / max(
                                len(reg_props), len(inline_props)
                            )
                            if score > best_score:
                                best_score = score
                                best_match = reg_name

            # Используем лучшее совпадение если точного не нашли
            if not found_schema and best_match and best_score > 0.8:
                found_schema = best_match

            if found_schema:
                if dependencies is not None:
                    dependencies.add(found_schema)
                resolved_name = self.schema_resolver.resolve_schema_name(
                    found_schema, zone, include_zone_prefix=False
                )
                return Variable(value=f'"{resolved_name}"')

            # Fallback - используем title как есть
            if dependencies is not None:
                dependencies.add(title)

            # Для развернутых inline схем пытаемся найти соответствующую зарегистрированную схему
            if "properties" in schema:
                properties = schema.get("properties", {})
                property_names = set(properties.keys())

                # Ищем наиболее подходящую зарегистрированную схему по совпадению полей
                best_match = None
                best_score = 0

                for reg_name, info in self.schema_resolver._schema_registry.items():
                    clean_name = info["clean_name"]
                    schema_zone = info["zone"]

                    # Получаем оригинальную схему из OpenAPI для сравнения полей
                    schemas = self.openapi_dict.get("components", {}).get("schemas", {})
                    if reg_name in schemas:
                        reg_schema = schemas[reg_name]
                        if (
                            reg_schema.get("type") == "object"
                            and "properties" in reg_schema
                        ):
                            reg_properties = set(reg_schema["properties"].keys())

                            # Считаем совпадающие поля
                            common_fields = property_names.intersection(reg_properties)
                            if (
                                len(common_fields) > best_score
                                and len(common_fields) >= 3
                            ):  # Минимум 3 поля
                                best_score = len(common_fields)
                                if schema_zone != zone and schema_zone != "common":
                                    best_match = f"{schema_zone}.{clean_name}"
                                else:
                                    best_match = clean_name

                if best_match:
                    resolved_name = best_match
                else:
                    # Fallback к стандартной логике
                    resolved_name = self.schema_resolver.resolve_schema_name(
                        title, zone, include_zone_prefix=False
                    )
            else:
                resolved_name = self.schema_resolver.resolve_schema_name(
                    title, zone, include_zone_prefix=False
                )

            return Variable(value=f'"{resolved_name}"')

        # Fallback к обычному типу
        return self._get_type(schema, zone)

    def _get_type_for_endpoint_parameter(self, schema: Dict) -> Variable:
        """Получение типа для endpoint параметра с полной поддержкой моделей"""
        if not schema:
            return Variable(value="Any")

        # Прямой $ref для endpoint параметров - ПРИОРИТЕТ 1
        if "$ref" in schema:
            ref_name = schema["$ref"].replace("#/components/schemas/", "")

            # Проверяем исходную схему - если это additionalProperties без properties, то это Dict
            schemas = self.openapi_dict.get("components", {}).get("schemas", {})
            if ref_name in schemas:
                ref_schema = schemas[ref_name]
                if (
                    ref_schema.get("type") == "object"
                    and "additionalProperties" in ref_schema
                    and not ref_schema.get("properties")
                ):
                    # Это Dict, а не модель
                    additional_props = ref_schema["additionalProperties"]
                    value_type = self._get_type_for_endpoint_parameter(additional_props)
                    return Variable(value=f"str, {value_type}", wrap_name="Dict")

            # Для endpoint параметров используем оригинальное имя с кросс-ссылками
            resolved_name = self.schema_resolver.resolve_schema_name(ref_name, "")
            return Variable(value=f'"{resolved_name}"')

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
                    # Для endpoint параметров используем кросс-ссылки
                    resolved_name = self.schema_resolver.resolve_schema_name(
                        ref_name, ""
                    )
                    types.append(Variable(value=f'"{resolved_name}"'))
                else:
                    types.append(self._get_type_for_endpoint_parameter(variant))

            if len(types) == 1:
                result = types[0]
            else:
                result = Variable(value=types, wrap_name="Union")

            if has_null:
                result = Variable(value=result, wrap_name="Optional")

            return result

        # Array с элементами
        if schema.get("type") == "array" and "items" in schema:
            items = schema["items"]
            if "$ref" in items:
                ref_name = items["$ref"].replace("#/components/schemas/", "")
                # Для endpoint параметров используем кросс-ссылки
                resolved_name = self.schema_resolver.resolve_schema_name(ref_name, "")
                return Variable(value=f'"{resolved_name}"', wrap_name="List")
            else:
                item_type = self._get_type_for_endpoint_parameter(items)
                return Variable(value=item_type, wrap_name="List")

        # Inline object с title (развернутая схема)
        if schema.get("type") == "object" and "title" in schema:
            # Проверяем additionalProperties - это должно быть Dict, а не модель
            if "additionalProperties" in schema:
                additional_props = schema["additionalProperties"]
                value_type = self._get_type_for_endpoint_parameter(additional_props)
                return Variable(value=f"str, {value_type}", wrap_name="Dict")

            title = schema["title"]
            # Пытаемся найти зарегистрированную схему по title
            resolved_name = self.schema_resolver.resolve_schema_name(title, "")
            return Variable(value=f'"{resolved_name}"')

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

    def _get_clean_model_type(self, responses: Dict, zone: str) -> str:
        """Получение чистого типа модели для response_model без Optional оберток"""
        # Если нет zone или zone = "common", ищем по первому найденному title
        if not zone or zone == "common":
            zone = None

        # Пытаемся использовать оригинальную спеку если она доступна
        # чтобы избежать проблем с jsonref который резолвит $ref
        for status_code, response_spec in responses.items():
            if status_code.startswith("2"):
                content = response_spec.get("content", {})
                if content:
                    for content_type, content_spec in content.items():
                        schema = content_spec.get("schema", {})

                        # Обработка anyOf/oneOf структур
                        if schema.get("anyOf") or schema.get("oneOf"):
                            variants = schema.get("anyOf", []) + schema.get("oneOf", [])
                            for variant in variants:
                                if "$ref" in variant:
                                    ref_name = variant["$ref"].replace(
                                        "#/components/schemas/", ""
                                    )
                                    clean_name = self._get_clean_schema_name(ref_name)
                                    # Возвращаем первую найденную модель без Optional
                                    return clean_name
                                elif (
                                    variant.get("type") == "object"
                                    and "title" in variant
                                ):
                                    # Инлайн объект с title
                                    title = variant["title"]
                                    # Ищем схему с таким title в правильной зоне
                                    for schema_name, schema_spec in (
                                        self.openapi_dict.get("components", {})
                                        .get("schemas", {})
                                        .items()
                                    ):
                                        if schema_spec.get("title") == title:
                                            schema_clean_name = (
                                                self._get_clean_schema_name(schema_name)
                                            )
                                            # Проверяем зону - очень гибкий поиск
                                            if zone:
                                                zone_lower = zone.lower()
                                                schema_lower = schema_clean_name.lower()
                                                title_lower = title.lower()

                                                # Ищем модель содержащую зону (или её часть) и title
                                                zone_match = (
                                                    zone_lower in schema_lower
                                                    or any(
                                                        part in schema_lower
                                                        for part in zone_lower.split(
                                                            "_"
                                                        )
                                                        if len(part) > 2
                                                    )
                                                )
                                                title_match = (
                                                    title_lower in schema_lower
                                                )

                                                if zone_match and title_match:
                                                    return schema_clean_name
                                            else:
                                                if schema_clean_name:
                                                    return schema_clean_name
                                    # Простой fallback
                                    return title
                        elif "$ref" in schema:
                            # Прямая ссылка на модель
                            ref_name = schema["$ref"].replace(
                                "#/components/schemas/", ""
                            )
                            clean_name = self._get_clean_schema_name(ref_name)
                            return clean_name
                        elif schema.get("type") == "array" and "items" in schema:
                            # Массив моделей - возвращаем тип элемента для response_model
                            items = schema["items"]
                            if "$ref" in items:
                                ref_name = items["$ref"].replace(
                                    "#/components/schemas/", ""
                                )
                                clean_name = self._get_clean_schema_name(ref_name)
                                # Для массивов возвращаем модель элемента, handle_request сам создаст список
                                return clean_name
                        elif schema.get("type") == "object" and "title" in schema:
                            # Проверяем additionalProperties - это должно быть Dict, а не модель
                            if "additionalProperties" in schema:
                                return (
                                    "dict"  # Для response_model используем обычный dict
                                )

                            # Инлайн объект с title
                            title = schema["title"]
                            # Ищем схему с таким title в текущей зоне
                            for schema_name, schema_spec in (
                                self.openapi_dict.get("components", {})
                                .get("schemas", {})
                                .items()
                            ):
                                if schema_spec.get("title") == title:
                                    # Проверяем что схема относится к правильной зоне
                                    schema_clean_name = self._get_clean_schema_name(
                                        schema_name
                                    )
                                    # Проверяем зону для всех схем
                                    if zone:
                                        # Используем гибкий поиск как в _get_return_type
                                        zone_lower = zone.lower()
                                        schema_lower = schema_clean_name.lower()
                                        title_lower = title.lower()

                                        # Ищем модель содержащую зону (или её часть) и title
                                        zone_match = zone_lower in schema_lower or any(
                                            part in schema_lower
                                            for part in zone_lower.split("_")
                                            if len(part) > 2
                                        )
                                        title_match = title_lower in schema_lower

                                        if zone_match and title_match:
                                            return schema_clean_name
                                    else:
                                        # Если нет зоны, возвращаем первую найденную
                                        if schema_clean_name:
                                            return schema_clean_name
                            # Fallback - используем title как есть
                            clean_name = self._get_clean_schema_name(title)
                            return clean_name
        return "Any"
