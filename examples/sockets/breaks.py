"""Пример использования WebSocket API перерывов."""

import asyncio
import logging
import os
from datetime import datetime

from dotenv import load_dotenv

from okc_py import OKC
from okc_py.sockets.models import (
    AuthMessage,
    PageData,
    SimplePageData,
    UserBreaks,
)

load_dotenv()
logging.basicConfig(level=logging.INFO)


def _print_header(text: str) -> None:
    """Print a formatted header."""
    print(f"\n{'=' * 60}")
    print(f"  {text}")
    print(f"{'=' * 60}")


def _print_subheader(text: str) -> None:
    """Print a formatted subheader."""
    print(f"\n{text}")
    print(f"{'-' * 40}")


def _on_auth_message(data: AuthMessage) -> None:
    """Обрабатывает подтверждение авторизации с валидацией через Pydantic."""
    _print_header("✅ Авторизация успешна")
    print(f"  Пользователь: {data.user_name}")
    print(f"  Супер-пользователь: {'Да' if data.is_super_user else 'Нет'}")


def _on_user_breaks(data: UserBreaks) -> None:
    """Обрабатывает количество перерывов пользователя с валидацией через Pydantic."""
    _print_header("💼 Ваши перерывы")
    print(f"  5-минутных:  {data.breaks_5}")
    print(f"  10-минутных: {data.breaks_10}")
    print(f"  15-минутных: {data.breaks_15}")
    print("  ──────────────────────")
    print(f"  Всего:        {data.total}")


def _on_page_data(data: PageData | SimplePageData) -> None:
    """Обрабатывает обновления перерывов с валидацией через Pydantic."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    _print_header(f"📊 Данные на {timestamp}")

    # Обрабатываем информацию по линиям
    for line_name, line_data in sorted(data.lines.items()):
        _print_subheader(f"📍 {line_name.upper()}")
        print(f"  Свободно перерывов: {line_data.break_number}")

        # Парсим пользователей на перерыве
        break_users = line_data.get_break_users()
        if break_users:
            print(f"\n  ☕ На перерыве ({len(break_users)}):")
            for user in break_users:
                print(f"     {user.number}. {user.employee_fullname} ({user.duration})")
        else:
            print("  ☕ На перерыве: никто")

        # Для ntp_nck пространства имен также показываем разгрузки
        if hasattr(line_data, "get_discharge_users"):
            discharge_users = line_data.get_discharge_users()  # type: ignore[attr-defined]
            if discharge_users:
                print(f"\n  📦 На разгрузке ({len(discharge_users)}):")
                for user in discharge_users:
                    print(
                        f"     {user.number}. {user.employee_fullname} ({user.duration})"
                    )

    # Парсим очередь операторов
    queue = data.parse_queue_operators()
    if queue:
        _print_subheader(f"⏳ Очередь ({len(queue)} операторов)")
        for operator in queue[:5]:
            delay_str = "Нет" if operator.delay == 0 else f"{operator.delay}"
            print(f"  {operator.number:2d}. {operator.fullname}")
            print(f"      Задержка: {delay_str} | Без отдыха: {operator.without_rest}")
        if len(queue) > 5:
            print(f"  ... и еще {len(queue) - 5} операторов")
    else:
        print("\n⏳ Очередь: пуста")


async def main():
    """Подключается к WebSocket и слушает обновления перерывов в реальном времени."""

    async with OKC(
        username=os.getenv("OKC_USERNAME"), password=os.getenv("OKC_PASSWORD")
    ) as client:
        # Получаем клиент для перерывов
        # Доступные пространства имен: ntp_one, ntp_two, ntp_nck
        breaks = client.ws.breaks.ntp_one

        # Подключаемся к WebSocket
        await breaks.connect()

        # Регистрируем обработчики для событий
        breaks.on("authMessage", _on_auth_message)
        breaks.on("userBreaks", _on_user_breaks)
        breaks.on("pageData", _on_page_data)

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
