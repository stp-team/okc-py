import asyncio

from okc_py import OKC


async def main():
    async with OKC(username="YOUR_USERNAME", password="YOUR_PASSWORD") as client:
        period = "1.12.2025"
        division = "НЦК"

        # Получить премиум специалиста
        specialist_premium = await client.premium.get_specialist_premium(
            period=period, division=division, employees_id=["employee_id_here"]
        )
        print(f"Specialist premium: {specialist_premium}")

        # Получить премиум руководителя.
        # Возвращаемый ответ отличается от ответа метода выше
        head_premium = await client.premium.get_head_premium(
            period=period, division=division, employees_id=["employee_id_here"]
        )
        print(f"Head premium: {head_premium}")


if __name__ == "__main__":
    asyncio.run(main())
