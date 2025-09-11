"""Утилиты для работы с именами полей и параметров"""

from typing import Dict, List


def extract_field_name_from_param(param_name: str, suffix: str) -> str:
    """
    Извлекает имя поля из имени параметра, правильно обрабатывая случаи
    когда суффикс уже содержится в оригинальном имени поля.

    Использует rfind() для поиска последнего вхождения суффикса,
    который был добавлен генератором.

    Args:
        param_name: Имя параметра (например, "request_body_body_1")
        suffix: Суффикс для удаления (например, "_body")

    Returns:
        Имя поля без суффикса (например, "request_body_1")

    Examples:
        >>> extract_field_name_from_param("field_name_body", "_body")
        'field_name'
        >>> extract_field_name_from_param("request_body_body_1", "_body")
        'request_body_1'
        >>> extract_field_name_from_param("field_query_2", "_query")
        'field_2'
    """
    if suffix in param_name:
        # Используем rfind чтобы найти последнее вхождение суффикса
        suffix_pos = param_name.rfind(suffix)
        base_name = param_name[:suffix_pos]
        remainder = param_name[suffix_pos + len(suffix) :]  # все после суффикса
        field_name = base_name + remainder if remainder else base_name
        return field_name
    else:
        return param_name


def filter_params_by_suffix(locals_dict: Dict[str, any], suffix: str) -> List[tuple]:
    """
    Фильтрует параметры по суффиксу, исключая NOTSET значения.

    Args:
        locals_dict: Словарь всех локальных переменных
        suffix: Суффикс для поиска (например, "_body", "_query", "_file")

    Returns:
        Список кортежей (param_name, value, field_name)
    """
    from ..generator.templates import is_not_set

    result = []
    for param_name, value in locals_dict.items():
        if suffix in param_name and param_name != "self" and not is_not_set(value):
            field_name = extract_field_name_from_param(param_name, suffix)
            result.append((param_name, value, field_name))

    return result


def create_field_mapping_entry(
    param_name: str, suffix: str, original_field_name: str
) -> tuple:
    """
    Создает запись для field_mapping из имени параметра.

    Args:
        param_name: Имя параметра (например, "field_name_body_1")
        suffix: Суффикс (например, "_body")
        original_field_name: Оригинальное имя поля из схемы

    Returns:
        Кортеж (field_name, original_field_name) или None если маппинг не нужен
    """
    field_name = extract_field_name_from_param(param_name, suffix)

    # Только если field_name отличается от original_field_name, создаем маппинг
    if field_name != original_field_name:
        return (field_name, original_field_name)

    return None
