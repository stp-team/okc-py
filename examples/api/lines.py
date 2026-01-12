import asyncio
import os

from dotenv import load_dotenv

from okc_py import OKC

load_dotenv()


async def main():
    async with OKC(
        username=os.getenv("OKC_USERNAME"), password=os.getenv("OKC_PASSWORD")
    ) as client:
        # Получить лог линии
        day_log = await client.api.lines.get_day_log(line_app_id=3)
        for message in day_log:
            print(
                f"[{message.active_from}] {message.employee_fullname}: {message.message_text}"
            )

        # Получить сотрудника
        user_data = await client.api.lines.get_user_data(employee_id=40472)
        if user_data:
            print(f"Сотрудник {user_data.data.employee_fullname}")

            if user_data.shift:
                for shift in user_data.shift:
                    print(f"Смена: {shift.shift_start} - {shift.shift_end}")

            if user_data.lunch:
                for lunch in user_data.lunch:
                    print(f"Обед: {lunch.lunch_start} - {lunch.lunch_end}")


if __name__ == "__main__":
    asyncio.run(main())
