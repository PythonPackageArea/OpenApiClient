from typing import Dict, Any

from ..types.models import Project
from ..generator.client_generator import ClientGenerator


class OpenApiParser:
    """Парсер OpenAPI спецификации"""

    def __init__(
        self,
        openapi_dict: Dict[str, Any],
        source_url: str = None,
        original_spec: Dict[str, Any] = None,
    ):
        self.openapi_dict = openapi_dict
        self.source_url = source_url
        self.original_spec = original_spec

    def parse(self) -> Project:
        """Парсинг OpenAPI в Project структуру"""
        generator = ClientGenerator(
            self.openapi_dict, self.source_url, self.original_spec
        )
        return generator.generate()
