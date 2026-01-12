"""Пример использования WebSocket API для линий ntp1/ntp2 (Cisco Finesse)."""

import asyncio
import logging
import os

from dotenv import load_dotenv

from okc_py import OKC
from okc_py.sockets.models import CiscoRawData, RawIncidents

load_dotenv()
logging.basicConfig(level=logging.INFO)


def _on_cisco_raw_data(data: dict) -> None:
    """Обрабатывает обновления данных линий Cisco Finesse (ntp1/ntp2)."""
    try:
        # Валидация данных через Pydantic модель для Cisco
        cisco_data = CiscoRawData(**data)

        # Статистика агентов
        ring_agents = len(cisco_data.cisco.ring)
        ready_agents = len(cisco_data.cisco.ready)
        talk_agents = len(cisco_data.cisco.talk)
        unknown_agents = len(cisco_data.cisco.unknown)

        total_waiting = sum(q.total for q in cisco_data.waitingQueue)
        total_talking = sum(q.total for q in cisco_data.talkingQueue)
        assignments = len(cisco_data.assignments)

        print(
            f"[Cisco] Агенты: {ring_agents} звонок, "
            f"{ready_agents} готово, {talk_agents} разговор, "
            f"{unknown_agents} неизвестно"
        )
        print(
            f"[Cisco] Очереди: {total_waiting} ожидание, "
            f"{total_talking} разговор, {assignments} назначения"
        )
        print(f"[Cisco] Дежурные: {[d.FIO for d in cisco_data.lineDuty]}")

        # Пример: показать первые 3 агента в разговоре
        if cisco_data.cisco.talk:
            print("[Cisco] Агенты на разговоре:")
            for agent in cisco_data.cisco.talk[:3]:
                print(f"  - {agent.userName} ({agent.state})")

        # Пример: показать назначения
        if cisco_data.assignments:
            print("[Cisco] Назначения:")
            for assign in cisco_data.assignments[:3]:
                print(f"  - {assign.userName}: {assign.state}")

    except Exception as e:
        print(f"[ERROR] Ошибка валидации Cisco RawData: {e}")


def _on_raw_incidents(data: dict) -> None:
    """Обрабатывает аварии (одинаковый формат для всех линий)."""
    try:
        incidents = RawIncidents(**data)

        priority_count = len(incidents.priority)
        new_count = len(incidents.new)
        old_count = len(incidents.old)

        print(
            f"[Incidents] Priority: {priority_count}, "
            f"New: {new_count}, Old: {old_count}"
        )

        # Показать приоритетные инциденты
        if incidents.priority:
            print("[Incidents] Приоритетные:")
            for inc in incidents.priority[:2]:
                desc_preview = (
                    (inc.description[:40] + "...") if inc.description else "N/A"
                )
                print(f"  - ID: {inc.incId}: {desc_preview}")

    except Exception as e:
        print(f"[ERROR] Ошибка валидации rawIncidents: {e}")


async def main():
    """Подключается к WebSocket ntp1 и слушает обновления Cisco Finesse."""

    async with OKC(
        username=os.getenv("OKC_USERNAME"), password=os.getenv("OKC_PASSWORD")
    ) as client:
        # Выберите линию: ntp1 или ntp2
        line = client.ws.lines.ntp1  # или .ntp2

        # Подключаемся к WebSocket
        await line.connect()

        # Регистрируем обработчики
        line.on("rawData", _on_cisco_raw_data)  # карта "raw" -> "rawData"
        line.on("rawIncidents", _on_raw_incidents)

        print(f"Статус подключения: {line.is_connected}")
        print("Линия: ntp1 (Cisco Finesse)")
        print("Нажмите Ctrl+C для остановки\n")

        # Держим соединение активным
        try:
            while True:
                await asyncio.sleep(1)
                if not line.is_connected:
                    print("\n[WARNING] WebSocket connection lost!")
                    break
        except KeyboardInterrupt:
            print("\nОтключение по запросу пользователя...")
        finally:
            await line.disconnect()
            print("WebSocket отключен")


if __name__ == "__main__":
    asyncio.run(main())
