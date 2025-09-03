import argparse
import json
import os
import sys

from openapi_client.internal.types.models import Project
from openapi_client.generator import ApiClientGenerator
from openapi_client.config import OpenApiConfig

import httpx
import jsonref


def confirm_choice(message: str) -> bool:
    """Запрос подтверждения у пользователя"""
    while True:
        choice = input(f"{message} (y/n): ").lower().strip()
        if choice in ["y", "yes", "да"]:
            return True
        elif choice in ["n", "no", "нет"]:
            return False
        print("Введите y/n")


def generate():
    """Универсальная команда генерации OpenAPI клиента"""
    parser = argparse.ArgumentParser(description="Генерация Python клиента из OpenAPI")
    parser.add_argument("--url", type=str, help="URL к OpenAPI спецификации")
    parser.add_argument("--dirname", type=str, help="Директория для генерации клиента")
    parser.add_argument(
        "--init-config", action="store_true", help="Создать конфиг файл openapi.toml"
    )
    parser.add_argument(
        "--force", action="store_true", help="Генерировать без подтверждения"
    )

    args = parser.parse_args()

    # Инициализация конфига
    if args.init_config:
        config = OpenApiConfig(
            url=args.url,
            dirname=args.dirname or "api_client",
        )
        config.save_to_file()
        print("✅ Создан конфиг файл openapi.toml")
        return

    # Загрузка конфига из файла
    file_config = OpenApiConfig.from_file(search_dir=args.dirname)

    # Определение финальной конфигурации
    if file_config and (args.url or args.dirname):
        # Есть и конфиг и аргументы - спрашиваем пользователя
        print("🔧 Найден конфиг файл openapi.toml:")
        print(f"   URL: {file_config.url}")
        print(f"   Директория: {file_config.dirname}")
        print()
        print("📝 Переданы аргументы:")
        if args.url:
            print(f"   URL: {args.url}")
        if args.dirname:
            print(f"   Директория: {args.dirname}")
        print()

        if args.force or confirm_choice("Использовать конфиг из файла?"):
            final_config = file_config
        else:
            final_config = file_config.merge_with_args(args)
    elif file_config:
        # Только конфиг (найден в указанной директории или текущей)
        config_location = "указанной директории" if args.dirname else "openapi.toml"
        print(f"📋 Используется конфиг из {config_location}")
        final_config = file_config
    elif args.url:
        # Только аргументы
        final_config = OpenApiConfig(url=args.url, dirname=args.dirname or "api_client")
    else:
        # Нет ни конфига ни URL
        print("❌ Ошибка: Укажите URL или создайте конфиг с --init-config")
        sys.exit(1)

    # Проверка обязательных параметров
    if not final_config.url:
        print("❌ Ошибка: URL не указан ни в конфиге, ни в аргументах")
        sys.exit(1)

    # Генерация клиента
    print(f"🚀 Генерация клиента из {final_config.url}")
    print(f"📁 Папка: {final_config.dirname}")

    try:
        # Загрузка OpenAPI спецификации
        print("📥 Загрузка OpenAPI спецификации...")
        openapi_spec = httpx.get(
            url=final_config.url
            + ("" if final_config.url.endswith("/") else "/")
            + "openapi.json"
        ).json()
        openapi_spec = dict(jsonref.loads(json.dumps(openapi_spec)))

        # Генерация
        print("⚙️ Генерация кода...")
        generator = ApiClientGenerator(openapi_spec, source_url=final_config.url)
        project: Project = generator.generate()

        # Сохранение файлов
        current_dir = os.getcwd()
        work_path = os.path.join(current_dir, final_config.dirname)

        print(f"💾 Сохранение {len(project.files)} файлов...")

        for code_model in project.files:
            path = os.path.join(work_path, code_model.file_name)
            os.makedirs(os.path.dirname(path), exist_ok=True)

            with open(path, "w") as f:
                f.write(str(code_model))

        print("✅ Генерация завершена успешно!")
        print(f"📦 Клиент создан в: {work_path}")

        # Обновление конфига если нужно
        if not file_config and (
            args.force or confirm_choice("Сохранить настройки в openapi.toml?")
        ):
            config_path = os.path.join(work_path, "openapi.toml")
            final_config.save_to_file(config_path)
            print(f"💾 Конфиг сохранен в {config_path}")

    except Exception as e:
        print(f"❌ Ошибка генерации: {e}")
        sys.exit(1)


# Deprecated функции для обратной совместимости
def gen():
    """Deprecated: используйте openapi-client"""
    print("⚠️ Команда gen-api устарела. Используйте: openapi-client")
    generate()


def update():
    """Deprecated: используйте openapi-client"""
    print("⚠️ Команда update-api устарела. Используйте: openapi-client")
    generate()


if __name__ == "__main__":
    generate()
