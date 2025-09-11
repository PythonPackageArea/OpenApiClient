"""Утилиты для генератора"""

from .field_utils import (
    extract_field_name_from_param,
    filter_params_by_suffix,
    create_field_mapping_entry,
)

__all__ = [
    "extract_field_name_from_param",
    "filter_params_by_suffix",
    "create_field_mapping_entry",
]
