import re


class SchemaNameResolver:
    """Резолвер имен схем для консистентности"""

    def __init__(self):
        self._schema_registry = {}

    def register_schema(self, original_name: str, clean_name: str, zone: str):
        """Регистрация схемы с чистым именем"""
        self._schema_registry[original_name] = {"clean_name": clean_name, "zone": zone}

    def resolve_schema_name(self, original_name: str, current_zone: str = "") -> str:
        """Получение чистого имени схемы с учетом зоны"""
        if original_name in self._schema_registry:
            info = self._schema_registry[original_name]
            schema_zone = info["zone"]
            clean_name = info["clean_name"]

            # Если схема из другой зоны, добавляем префикс зоны для кросс-ссылок
            if current_zone and schema_zone != current_zone and schema_zone != "common":
                return f"{schema_zone}.{clean_name}"

            return clean_name

        # Fallback - создаем имя на лету
        fallback = self._clean_schema_name(original_name)

        # Если это простое имя вроде Read, Create и т.д. и есть current_zone,
        # попробуем создать зонное имя
        if (
            original_name in ["Read", "Create", "Update", "Delete", "Paginated"]
            and current_zone
            and current_zone != "common"
        ):
            zone_fallback = f"{current_zone.capitalize()}{original_name}"
            # Проверяем есть ли такая схема в реестре
            for reg_name, info in self._schema_registry.items():
                if info["clean_name"] == zone_fallback and info["zone"] == current_zone:
                    return zone_fallback

        return fallback

    def get_schema_zone(self, original_name: str) -> str:
        """Получение зоны схемы"""
        if original_name in self._schema_registry:
            return self._schema_registry[original_name]["zone"]
        return "common"

    def is_cross_zone_reference(self, original_name: str, current_zone: str) -> bool:
        """Проверка нужен ли кросс-импорт для этой схемы"""
        if original_name in self._schema_registry:
            schema_zone = self._schema_registry[original_name]["zone"]
            return (
                current_zone and schema_zone != current_zone and schema_zone != "common"
            )
        return False

    @staticmethod
    def _clean_schema_name(name: str) -> str:
        """Очистка имени схемы с правильным PascalCase"""
        if name.startswith("app__services__"):
            # app__services__accounts__schemas__Accounts__Read → AccountsRead
            parts = name.split("__")
            if len(parts) >= 5:
                service = parts[2]  # accounts
                operation = parts[-1]  # Read
                return f"{service.capitalize()}{operation.capitalize()}"

        # Для простых имен типа LoginResponse, UserShort - оставляем как есть если уже PascalCase
        if name and name[0].isupper() and not "_" in name:
            return name

        # Обычная очистка с правильным PascalCase
        clean = re.sub(r"[^a-zA-Z0-9]", "_", name)
        parts = []

        for part in clean.split("_"):
            if not part:
                continue
            if part.upper() in ["HTTP", "API", "URL", "JSON", "XML", "HTML"]:
                parts.append(part.upper())
            elif part.lower() == "id":
                parts.append("ID")
            else:
                parts.append(part.capitalize())

        return "".join(parts)
