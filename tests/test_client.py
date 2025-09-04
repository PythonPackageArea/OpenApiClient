"""
Тест нового клиента с прямым доступом к зонам
"""

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "api_client"))
from api_client import ApiClient
import asyncio

client = ApiClient()


async def main():
    # Настраиваем клиент
    client.initialize("http://127.0.0.1:8000")

    try:
        login_response = await client.authentication.login(
            username_body="user", password_body="Ls27jTmr"
        )
        print(f"✅ Login response: {login_response}")
        print(f"Type: {type(login_response)}")
        await client.close()
        client._headers.update(Authorization=f"Bearer {login_response.token}")

        # print(client._headers)

        # upload_response = await client.uploads.upload_strings()
        # print(f"Upload response class: {upload_response.__class__}")
        # print(f"✅ Upload response: {upload_response}")
        # print(f"Type: {type(upload_response)}")

        # groups_response = await client.groups.find_many()
        # print(f"Groups response class: {groups_response.__class__}")
        # print(f"Has .data attribute: {hasattr(groups_response, 'data')}")
        # print(f"✅ Groups response: {groups_response}")
        # print(f"Type: {type(groups_response)}")

        # sessions_response = await client.sessions.find_many()
        # print(f"Sessions response class: {sessions_response.__class__}")
        # print(f"Has .data attribute: {hasattr(sessions_response, 'data')}")
        # print(f"✅ Sessions response: {sessions_response}")
        # print(f"Type: {type(sessions_response)}")

        # for session in sessions_response.data:  # Берем только первые 3
        #     if session.account:  # Проверяем что account не None
        #         account = session.account
        #         print(f"✅ Account phone: {account.get('phone', 'N/A')}")
        #         print(f"Account type: {type(account)}")
        #     else:
        #         print("Account is None")
        #     # break  # Проверяем только первую сессию

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())


def test_direct_zone_access_integration():
    """Интеграционный тест прямого доступа к зонам"""
    import sys
    import os

    # Добавляем test_clean в путь
    test_path = os.path.join(os.getcwd(), "test_clean")
    if test_path not in sys.path:
        sys.path.insert(0, test_path)

    try:
        from api_client import ApiClient

        client = ApiClient()

        # Прямой доступ к зонам
        assert hasattr(client, "accounts")
        assert hasattr(client, "authentication")
        assert hasattr(client, "sessions")

        # Проверяем типы зон
        assert type(client.accounts).__name__ == "Accounts"
        assert type(client.authentication).__name__ == "Authentication"

        # Методы в зонах
        assert hasattr(client.accounts, "find_many_accounts")
        assert hasattr(client.authentication, "login")

        # Прямой доступ к методам
        assert hasattr(client, "login")
        assert hasattr(client, "find_many_accounts")

        print("✅ Все проверки прямого доступа пройдены!")
        return True

    except Exception as e:
        print(f"❌ Ошибка в тесте: {e}")
        return False


# if __name__ == "__main__":
#     success = test_direct_zone_access_integration()
#     if success:
#         print("🎉 Тест клиента успешно пройден!")
#     else:
#         print("❌ Тест клиента не пройден")
