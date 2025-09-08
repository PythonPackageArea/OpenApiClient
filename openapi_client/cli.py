import argparse
import json
import os
import sys
import glob
from typing import List, Tuple, Optional

from openapi_client.internal.types.models import Project
from openapi_client.generator import ApiClientGenerator
from openapi_client.config import OpenApiConfig

import httpx
import jsonref


def confirm_choice(message: str) -> bool:
    """Запрос подтверждения у пользователя"""
    while True:
        choice = input(f"{message} (y/n): ").lower().strip()
        if choice in ["y", "yes", "да", ""]:
            return True
        elif choice in ["n", "no", "нет"]:
            return False
        print("Введите y/n")


def find_client_packages() -> List[Tuple[str, OpenApiConfig]]:
    """Поиск клиент-пакетов по openapi.toml файлам"""
    packages = []

    # Поиск всех openapi.toml файлов рекурсивно
    for config_file in glob.glob("**/openapi.toml", recursive=True):
        config_dir = os.path.dirname(config_file)
        config = OpenApiConfig.from_file(config_file)

        if config:
            packages.append((config_dir, config))

    return packages


def select_from_menu(options: List[str], title: str) -> int:
    """Выбор пункта из меню"""
    print(f"\n{title}")
    for i, option in enumerate(options, 1):
        print(f"[{i}] {option}")

    while True:
        try:
            choice = int(input("\nВыберите пункт: "))
            if 1 <= choice <= len(options):
                return choice - 1
            print(f"Введите число от 1 до {len(options)}")
        except ValueError:
            print("Введите корректное число")


def interactive_find_packages():
    """Интерактивный поиск и обновление клиент-пакетов"""
    print("🔍 Поиск клиент-пакетов...")
    packages = find_client_packages()

    if not packages:
        print("❌ Клиент-пакеты не найдены")
        return

    print(f"✅ Найдено {len(packages)} клиент-пакетов:")

    package_options = []
    for config_dir, config in packages:
        package_options.append(f"{config_dir} ({config.url})")

    selected_idx = select_from_menu(package_options, "📦 Найденные клиент-пакеты:")
    selected_dir, selected_config = packages[selected_idx]

    print(f"\n📍 Выбран пакет: {selected_dir}")
    print(f"   URL: {selected_config.url}")
    print(f"   Директория: {selected_config.dirname}")

    # Меню действий
    action_options = [
        "Обновить генерацию",
        "Изменить ссылку и обновить",
    ]

    action = select_from_menu(action_options, "\n⚙️ Что сделать с пакетом?")

    if action == 0:  # Обновить генерацию
        _generate_client_in_existing(selected_config, selected_dir)
    elif action == 1:  # Изменить ссылку
        new_url = input(f"\n🔗 Введите новый URL (текущий: {selected_config.url}): ")
        if new_url.strip():
            selected_config.url = new_url.strip()
            config_path = os.path.join(selected_dir, "openapi.toml")
            selected_config.save_to_file(config_path)
            print(f"💾 URL обновлен в {config_path}")

        _generate_client_in_existing(selected_config, selected_dir)


def interactive_create_package():
    """Интерактивное создание нового пакета"""
    print("\n📦 Создание нового клиент-пакета")

    # 1. Запрос названия пакета (первым!)
    package_name = input("📦 Введите название пакета [api_client]: ").strip()
    if not package_name:
        package_name = "api_client"

    # 2. Запрос пути до директории
    target_dir = input("📁 Введите путь до директории: ").strip()
    if not target_dir:
        print("❌ Путь не указан")
        return

    # Проверка существования директории
    if not os.path.exists(target_dir):
        if confirm_choice(f"Директория {target_dir} не существует. Создать?"):
            try:
                os.makedirs(target_dir, exist_ok=True)
                print(f"✅ Директория {target_dir} создана")
            except Exception as e:
                print(f"❌ Ошибка создания директории: {e}")
                return
        else:
            return

    # 3. Запрос URL к OpenAPI спецификации
    url = input("🔗 Введите URL к OpenAPI спецификации: ").strip()
    if not url:
        print("❌ URL не указан")
        return

    # Используем название пакета как имя директории
    client_dirname = package_name

    # Подтверждение
    print("\n📋 Параметры создания:")
    print(f"   Название пакета: {package_name}")
    print(f"   Путь: {target_dir}")
    print(f"   URL: {url}")
    print(f"   Директория клиента: {client_dirname}")

    if not confirm_choice("Все правильно?"):
        return

    # Создание и генерация
    config = OpenApiConfig(url=url, dirname=client_dirname)

    # Переход в целевую директорию
    original_cwd = os.getcwd()
    try:
        os.chdir(target_dir)
        _generate_client(config, ".")

        # Сохранение конфига
        config_path = os.path.join(client_dirname, "openapi.toml")
        config.save_to_file(config_path)
        print(f"💾 Конфиг сохранен в {config_path}")

    finally:
        os.chdir(original_cwd)


def _generate_client_core(config: OpenApiConfig) -> Project:
    """Ядро генерации клиента - только генерация без сохранения"""
    if not config.url:
        raise ValueError("URL не указан в конфигурации")

    print(f"🚀 Генерация клиента из {config.url}")

    # Загрузка OpenAPI спецификации
    print("📥 Загрузка OpenAPI спецификации...")

    # Проверяем - это локальный файл или URL
    if config.url.startswith(("http://", "https://")):
        # Это URL - загружаем по HTTP
        openapi_spec = httpx.get(
            url=config.url + ("" if config.url.endswith("/") else "/") + "openapi.json"
        ).json()
    elif os.path.exists(config.url):
        # Это локальный файл - читаем его
        with open(config.url, "r", encoding="utf-8") as f:
            openapi_spec = json.load(f)
    else:
        # Попробуем как URL без протокола
        try:
            openapi_spec = httpx.get(
                url="https://"
                + config.url
                + ("" if config.url.endswith("/") else "/")
                + "openapi.json"
            ).json()
        except:
            raise ValueError(
                f"Не удалось загрузить спецификацию из {config.url}. Проверьте URL или путь к файлу."
            )

    # Сохраняем оригинальную спецификацию до разрешения ссылок
    original_spec = openapi_spec.copy()
    openapi_spec = dict(jsonref.loads(json.dumps(openapi_spec)))

    # Генерация
    print("⚙️ Генерация кода...")
    generator = ApiClientGenerator(
        openapi_spec, source_url=config.url, original_spec=original_spec
    )
    return generator.generate()


def _save_project_files(project: Project, target_path: str):
    """Сохранение файлов проекта"""
    print(f"💾 Сохранение {len(project.files)} файлов...")

    for code_model in project.files:
        path = os.path.join(target_path, code_model.file_name)
        os.makedirs(os.path.dirname(path), exist_ok=True)

        with open(path, "w") as f:
            f.write(str(code_model))

    print("✅ Генерация завершена успешно!")
    print(f"📦 Клиент создан в: {os.path.abspath(target_path)}")


def _generate_client(config: OpenApiConfig, work_dir: str):
    """Генерация клиента в новую директорию"""
    if not config.dirname:
        raise ValueError("Директория не указана в конфигурации")

    try:
        project = _generate_client_core(config)
        work_path = os.path.join(work_dir, config.dirname)
        _save_project_files(project, work_path)

    except Exception as e:
        print(f"❌ Ошибка генерации: {e}")
        raise


def _generate_client_in_existing(config: OpenApiConfig, existing_package_dir: str):
    """Генерация клиента в существующую директорию пакета"""
    try:
        project = _generate_client_core(config)
        _save_project_files(project, existing_package_dir)

    except Exception as e:
        print(f"❌ Ошибка генерации: {e}")
        raise


def interactive_menu():
    """Главное интерактивное меню"""
    print("🎯 OpenAPI Client Generator")

    menu_options = ["Рекурсивно найти клиент-пакеты", "Создать пакет"]

    choice = select_from_menu(menu_options, "📋 Выберите действие:")

    if choice == 0:
        interactive_find_packages()
    elif choice == 1:
        interactive_create_package()


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

    # Проверка на интерактивный режим (нет аргументов)
    if not any(vars(args).values()):
        interactive_menu()
        return

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
    if args.dirname and file_config:
        print(f"📁 Генерация в существующую папку: {args.dirname}")
    else:
        print(f"📁 Создание новой папки: {final_config.dirname}")

    try:
        # Если указан dirname через аргументы и найден конфиг в этой директории,
        # генерируем прямо в эту директорию
        if args.dirname and file_config:
            _generate_client_in_existing(final_config, args.dirname)
        else:
            _generate_client(final_config, ".")

        # Обновление конфига если нужно
        if args.dirname and file_config:
            work_path = args.dirname
        else:
            work_path = os.path.join(os.getcwd(), final_config.dirname)
        if not file_config and (
            args.force or confirm_choice("Сохранить настройки в openapi.toml?")
        ):
            config_path = os.path.join(work_path, "openapi.toml")
            final_config.save_to_file(config_path)
            print(f"💾 Конфиг сохранен в {config_path}")

    except Exception as e:
        print(f"❌ Ошибка генерации: {e}")
        sys.exit(1)


if __name__ == "__main__":
    generate()
