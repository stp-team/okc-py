"""Пример одновременного подключения к нескольким линиям."""

import asyncio
import logging
import os

from dotenv import load_dotenv

from okc_py import OKC
from okc_py.sockets import RawData

load_dotenv()
logging.basicConfig(level=logging.INFO)


async def listen_to_line(line_name: str, line_client, duration: int = 30):
    """Слушает события от конкретной линии.

    Args:
        line_name: Название линии для логирования
        line_client: WebSocket клиент линии
        duration: Длительность прослушивания в секундах
    """

    def on_raw_data(data: dict) -> None:
        try:
            raw_data = RawData(**data)
            ready_count = len(raw_data.agents.readyAgents)
            print(f"[{line_name}] Агентов готово: {ready_count}, SL: {raw_data.daySl}%")
        except Exception as e:
            print(f"[{line_name}] ERROR: {e}")

    await line_client.connect()
    line_client.on("rawData", on_raw_data)

    print(f"[{line_name}] Подключено к {line_client._namespace}")

    try:
        for _ in range(duration):
            await asyncio.sleep(1)
            if not line_client.is_connected:
                print(f"[{line_name}] Соединение потеряно!")
                break
    finally:
        await line_client.disconnect()
        print(f"[{line_name}] Отключено")


async def main():
    """Подключается к нескольким линиям одновременно."""

    async with OKC(
        username=os.getenv("OKC_USERNAME"), password=os.getenv("OKC_PASSWORD")
    ) as okc:
        # Получаем клиенты для разных линий
        nck = okc.ws.nck
        ntp1 = okc.ws.ntp1
        ntp2 = okc.ws.ntp2

        print("Запуск одновременного подключения к 3 линиям...")

        # Запускаем все подключения параллельно
        await asyncio.gather(
            listen_to_line("NCK", nck, duration=10),
            listen_to_line("NTP1", ntp1, duration=10),
            listen_to_line("NTP2", ntp2, duration=10),
        )

        print("\nВсе подключения завершены")


if __name__ == "__main__":
    asyncio.run(main())
