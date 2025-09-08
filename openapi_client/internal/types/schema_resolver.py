import re


class SchemaNameResolver:
    """Резолвер имен схем для консистентности"""

    def __init__(self):
        self._schema_registry = {}

    def register_schema(self, original_name: str, clean_name: str, zone: str):
        """Регистрация схемы с чистым именем"""
        self._schema_registry[original_name] = {"clean_name": clean_name, "zone": zone}

    def resolve_schema_name(
        self,
        original_name: str,
        current_zone: str = "",
        include_zone_prefix: bool = True,
    ) -> str:
        """Получение чистого имени схемы с учетом зоны"""
        if original_name in self._schema_registry:
            info = self._schema_registry[original_name]
            schema_zone = info["zone"]
            clean_name = info["clean_name"]

            # Если схема из другой зоны, добавляем префикс зоны для кросс-ссылок
            if (
                include_zone_prefix
                and current_zone
                and schema_zone != current_zone
                and schema_zone != "common"
            ):
                return f"{schema_zone}.{clean_name}"

            # Специальная логика для общих схем в common зоне
            if schema_zone == "common" and current_zone and current_zone != "common":
                # Для общих имен типа "Counts" пытаемся найти зонную версию
                if clean_name in ["Counts"]:
                    zone_variant = f"{current_zone.capitalize()}{clean_name}"
                    # Проверяем есть ли такая зонная схема
                    for reg_name, reg_info in self._schema_registry.items():
                        if (
                            reg_info["clean_name"] == zone_variant
                            and reg_info["zone"] == current_zone
                        ):
                            return zone_variant
                    # Если нет зонной версии, возвращаем с префиксом зоны
                    return zone_variant

            return clean_name

        # Fallback - создаем имя на лету
        fallback = self._clean_schema_name(original_name)

        # Универсальная логика для любых имен - сначала проверяем зонную версию в текущей зоне
        if current_zone and current_zone != "common":
            zone_variant = f"{current_zone.capitalize()}{original_name}"
            for reg_name, info in self._schema_registry.items():
                if info["clean_name"] == zone_variant and info["zone"] == current_zone:
                    return zone_variant

        # Ищем точное совпадение в других зонах
        for reg_name, info in self._schema_registry.items():
            if info["clean_name"].endswith(original_name):
                schema_zone = info["zone"]
                clean_name = info["clean_name"]
                # Если это другая зона, возвращаем с префиксом
                if (
                    include_zone_prefix
                    and current_zone
                    and schema_zone != current_zone
                    and schema_zone != "common"
                ):
                    return f"{schema_zone}.{clean_name}"

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
        """Универсальная очистка имени схемы с правильным PascalCase"""
        # Универсальная обработка ____Schemas____ структур
        if "____Schemas____" in name or "____Schemas__" in name:
            # Разбиваем по разным вариантам паттерна
            if "____Schemas____" in name:
                parts = name.split("____Schemas____")
            else:
                parts = name.split("____Schemas__")

            if len(parts) == 2:
                prefix_parts = [p for p in parts[0].split("__") if p]
                suffix = parts[1].strip("__")

                # Берем предпоследнюю значимую часть как зону
                if len(prefix_parts) >= 2:
                    zone = prefix_parts[-2].capitalize()

                    # Создаем итоговое имя: Bots + Create = BotsCreate
                    if suffix:
                        return f"{zone}{suffix}"

                # Fallback - только suffix
                if suffix:
                    return suffix

        # Универсальная обработка многоуровневых структур с __
        if "__" in name and len(name.split("__")) >= 3:
            parts = [p for p in name.split("__") if p]  # убираем пустые части

            # Ищем часть schemas и берем соседние части
            for i, part in enumerate(parts):
                if part.lower() == "schemas":
                    # Ищем зону и операцию после schemas
                    if i < len(parts) - 2:
                        zone = parts[i + 1].capitalize()
                        operation = parts[i + 2].capitalize()
                        # Возвращаем ZoneOperation (например BotsCreate)
                        return f"{zone}{operation}"

            # Fallback - берем последние 2 значимые части (зона + тип операции)
            if len(parts) >= 2:
                # Исключаем очевидно служебные части (короткие или повторяющиеся)
                meaningful_parts = []
                for part in parts:
                    # Исключаем части которые повторяются в других частях имени
                    if len(part) >= 2 and part.lower() not in [
                        p.lower() for p in meaningful_parts
                    ]:
                        meaningful_parts.append(part.capitalize())

                if len(meaningful_parts) >= 2:
                    # Берем последние 2 части: зону + операцию
                    return "".join(meaningful_parts[-2:])
                elif meaningful_parts:
                    return meaningful_parts[-1]

        # Универсальная обработка имен с пробелами
        if " " in name:
            words = [w for w in name.split() if w]  # убираем пустые части

            # Если первое слово указывает на тип схемы, обрабатываем специально
            if len(words) >= 2:
                first_word = words[0].lower()

                # Универсальная логика для схем с типом (первое слово определяет тип)
                # Если первое слово короткое и может быть типом схемы
                if len(first_word) <= 8 and first_word.isalpha():
                    # Берем первые значимые слова после типа
                    meaningful_words = words[1:]

                    if len(meaningful_words) >= 2:
                        return f"{meaningful_words[0]}{meaningful_words[1]}{first_word.capitalize()}"
                    elif len(meaningful_words) == 1:
                        return f"{meaningful_words[0]}{first_word.capitalize()}"

            # Fallback - просто склеиваем все слова
            return "".join([word.capitalize() for word in words if word])

        # Для простых имен типа LoginResponse, UserShort - оставляем как есть если уже PascalCase и нет спецсимволов
        if name and name[0].isupper() and not "_" in name and not "-" in name:
            return name

        # Универсальная очистка имен с underscores или дефисами
        if "_" in name or "-" in name:
            # Заменяем дефисы на underscores для единообразной обработки
            name = name.replace("-", "_")
            parts = []
            for part in name.split("_"):
                if not part:
                    continue
                # Универсальная логика: если часть уже в верхнем регистре, оставляем как есть
                if part.isupper() and len(part) <= 4:  # аббревиатуры типа HTTP, API
                    parts.append(part)
                # Если часть 'id' в любом регистре, делаем 'ID'
                elif part.lower() == "id":
                    parts.append("ID")
                else:
                    parts.append(part.capitalize())
            return "".join(parts)

        # Fallback - capitalize первую букву
        return name.capitalize() if name else "Model"
