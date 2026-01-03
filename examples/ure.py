import asyncio

from okc_py import OKC


async def main():
    async with OKC(username="YOUR_USERNAME", password="YOUR_PASSWORD") as client:
        # Доступные юниты
        print(f"Unites: {client.ure.unites}")

        # Доступные репорты
        print(f"Reports: {client.ure.reports}")

        # Получить назначенные тесты
        division = "НЦК"
        report_type = "AHT"

        # Показатели за последний день
        day_report = await client.ure.get_day_kpi(division=division, report=report_type)
        print(f"Daily KPI: {day_report}")

        # Показатели за последнюю неделю
        week_report = await client.ure.get_week_kpi(
            division=division, report=report_type
        )
        print(f"Weekly KPI: {week_report}")

        # Показатели за последний месяц
        month_report = await client.ure.get_month_kpi(
            division=division, report=report_type
        )
        print(f"Monthly KPI: {month_report}")


if __name__ == "__main__":
    asyncio.run(main())
