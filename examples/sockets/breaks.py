"""Пример использования WebSocket API перерывов."""

import asyncio
import logging
import os

from dotenv import load_dotenv

from okc_py import OKC

load_dotenv()
logging.basicConfig(level=logging.INFO)


def _on_break_update(data: dict) -> None:
    """Обрабатывает обновления перерывов."""
    print(f"[breakUpdate] Данные: {data}")


async def main():
    """Подключается к WebSocket и слушает обновления перерывов в реальном времени."""

    async with OKC(
        username=os.getenv("OKC_USERNAME"), password=os.getenv("OKC_PASSWORD")
    ) as client:
        # Получаем клиент для перерывов
        breaks = client.ws.breaks

        # Подключаемся к WebSocket
        await breaks.connect()

        # Регистрируем обработчики для событий
        breaks.on("breakUpdate", _on_break_update)

        print(f"Статус подключения: {breaks.is_connected}")
        print("Нажмите Ctrl+C для остановки\n")

        # Держим соединение активным
        try:
            while True:
                await asyncio.sleep(1)
                if not breaks.is_connected:
                    print("\n[WARNING] WebSocket connection lost!")
                    break
        except KeyboardInterrupt:
            print("\nОтключение по запросу пользователя...")
        finally:
            await breaks.disconnect()
            print("WebSocket отключен")


if __name__ == "__main__":
    asyncio.run(main())
