"""
Тесты для системы конфигурации
"""

import os
import tempfile
import pytest
from api_to_client.config import OpenApiConfig


class TestOpenApiConfig:
    """Тесты конфигурации OpenAPI"""

    def test_config_creation(self):
        """Тест создания конфигурации"""
        config = OpenApiConfig(url="http://localhost:8000", dirname="test_client")

        assert config.url == "http://localhost:8000"
        assert config.dirname == "test_client"

    def test_config_save_and_load(self):
        """Тест сохранения и загрузки конфигурации"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = os.path.join(temp_dir, "test_openapi.toml")

            # Создаем и сохраняем конфиг
            original_config = OpenApiConfig(
                url="http://api.example.com", dirname="example_client"
            )
            original_config.save_to_file(config_path)

            # Загружаем конфиг
            loaded_config = OpenApiConfig.from_file(config_path)

            assert loaded_config is not None
            assert loaded_config.url == "http://api.example.com"
            assert loaded_config.dirname == "example_client"

    def test_config_file_not_exists(self):
        """Тест загрузки несуществующего конфига"""
        config = OpenApiConfig.from_file("nonexistent.toml")
        assert config is None

    def test_config_merge_with_args(self):
        """Тест объединения конфига с аргументами"""
        config = OpenApiConfig(url="http://localhost:8000", dirname="original_client")

        # Мокаем args
        class MockArgs:
            def __init__(self):
                self.url = "http://api.new.com"
                self.dirname = None

        args = MockArgs()
        merged = config.merge_with_args(args)

        assert merged.url == "http://api.new.com"  # Переписан из args
        assert merged.dirname == "original_client"  # Остался из config

    def test_default_values(self):
        """Тест значений по умолчанию"""
        config = OpenApiConfig()

        assert config.url is None
        assert config.dirname is None
