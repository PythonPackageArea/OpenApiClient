"""
Конфигурация для генерации API клиента
"""

import os
from typing import Dict, Any, Optional
import toml
from dataclasses import dataclass


@dataclass
class OpenApiConfig:
    """Конфигурация генератора OpenAPI клиента"""

    url: Optional[str] = None
    dirname: Optional[str] = None

    @classmethod
    def from_file(
        cls, config_path: str = "openapi.toml", search_dir: str = None
    ) -> Optional["OpenApiConfig"]:
        """Загрузка конфигурации из файла"""
        # Если указана директория для поиска, ищем конфиг там
        if search_dir and os.path.isdir(search_dir):
            config_in_dir = os.path.join(search_dir, "openapi.toml")
            if os.path.exists(config_in_dir):
                config_path = config_in_dir

        if not os.path.exists(config_path):
            return None

        try:
            config_data = toml.load(config_path)
            return cls(
                url=config_data.get("url"),
                dirname=config_data.get("dirname", "api_client"),
            )
        except Exception:
            return None

    def save_to_file(self, config_path: str = "openapi.toml") -> None:
        """Сохранение конфигурации в файл"""
        config_data = {
            "url": self.url,
            "dirname": self.dirname,
        }

        with open(config_path, "w") as f:
            toml.dump(config_data, f)

    def merge_with_args(self, args) -> "OpenApiConfig":
        """Объединение с аргументами командной строки"""
        return OpenApiConfig(
            url=args.url or self.url,
            dirname=args.dirname or self.dirname,
        )
