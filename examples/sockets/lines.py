"""Пример использования WebSocket API линий."""

import asyncio
import logging
import os

from dotenv import load_dotenv

from okc_py import OKC
from okc_py.sockets.models import RawData, RawIncidents

load_dotenv()
logging.basicConfig(level=logging.INFO)


def _on_raw_data(data: dict) -> None:
    """Обрабатывает обновления данных линий с валидацией через Pydantic."""
    try:
        # Валидация данных через Pydantic модель
        raw_data = RawData(**data)

        ready_agents = len(raw_data.agents.readyAgents)
        not_ready_agents = len(raw_data.agents.notReadyAgents)
        assign_agents = len(raw_data.agents.assignAgents)
        break_agents = len(raw_data.agents.breakAgents)

        total_waiting = sum(
            q.current_waiting_calls for level in raw_data.availQueues for q in level
        )

        cities_in_process = raw_data.citiesInProcess.total

        print(
            f"[rawData] Агентов: {ready_agents} готово, "
            f"{not_ready_agents} не готово, "
            f"{assign_agents} в назначении, "
            f"{break_agents} на перерыве"
        )
        print(
            f"[rawData] В очереди: {total_waiting} | "
            f"В обработке: {cities_in_process} чатов"
        )
        print(f"[rawData] SL за день: {raw_data.daySl}%")
        print(f"[rawData] Дежурные: {[d.FIO for d in raw_data.lineDuty]}")

        # Пример доступа к конкретному городу
        samara_status = raw_data.citiesStatuses.samara
        if samara_status.all != "0":
            print(
                f"[rawData] Самара: {samara_status.ruName} - {samara_status.Mobile_chat}"
            )

    except Exception as e:
        print(f"[ERROR] Ошибка валидации rawData: {e}")


def _on_raw_incidents(data: dict) -> None:
    """Обрабатывает аварии с валидацией через Pydantic."""
    try:
        # Валидация данных через Pydantic модель
        incidents = RawIncidents(**data)

        priority_count = len(incidents.priority)
        new_count = len(incidents.new)
        old_count = len(incidents.old)

        print(
            f"[rawIncidents] Priority: {priority_count}, "
            f"New: {new_count}, Old: {old_count}"
        )

        # Если есть приоритетные инциденты, покажем детали
        if incidents.priority:
            print("[rawIncidents] Приоритетные инциденты:")
            for inc in incidents.priority[:3]:  # Показываем первые 3
                desc_preview = inc.description[:30] if inc.description else "N/A"
                print(f"  - ID: {inc.incId}, Описание: {desc_preview}...")

        # Статистика по новым/старым
        if incidents.new:
            total_new = sum(
                stat.mobile + stat.office + stat.other for stat in incidents.new
            )
            print(f"[rawIncidents] Всего новых: {total_new}")

        if incidents.old:
            total_old = sum(
                stat.mobile + stat.office + stat.other for stat in incidents.old
            )
            print(f"[rawIncidents] Всего старых: {total_old}")

    except Exception as e:
        print(f"[ERROR] Ошибка валидации rawIncidents: {e}")


async def main():
    """Подключается к WebSocket и слушает обновления линий в реальном времени."""

    async with OKC(
        username=os.getenv("OKC_USERNAME"), password=os.getenv("OKC_PASSWORD")
    ) as client:
        # Выберите линию для подключения: nck, ntp1, ntp2
        line = client.ws.lines.nck  # или .ntp1, .ntp2

        # Подключаемся к WebSocket
        await line.connect()

        # Регистрируем обработчики для конкретных событий
        line.on("rawData", _on_raw_data)
        line.on("rawIncidents", _on_raw_incidents)

        print(f"Статус подключения: {line.is_connected}")
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
