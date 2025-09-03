"""
Главный модуль генератора - чистый интерфейс
"""

from typing import Dict, Any

from .internal.parser.openapi import OpenApiParser
from .internal.types.models import Project


class ApiClientGenerator:
    """Чистый интерфейс для генерации API клиентов"""

    def __init__(self, openapi_spec: Dict[str, Any], source_url: str = None):
        self.parser = OpenApiParser(openapi_spec, source_url)

    def generate(self) -> Project:
        """Генерация проекта клиента"""
        return self.parser.parse()


# Backward compatibility
def generate_client(openapi_spec: Dict[str, Any], source_url: str = None) -> Project:
    """Создание API клиента из OpenAPI спецификации"""
    generator = ApiClientGenerator(openapi_spec, source_url)
    return generator.generate()
