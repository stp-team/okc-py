import asyncio
import os

from dotenv import load_dotenv

from okc_py import OKC

load_dotenv()


async def main():
    async with OKC(
        username=os.getenv("OKC_USERNAME"), password=os.getenv("OKC_PASSWORD")
    ) as client:
        # Получить конкретного сотрудника. Поиск либо по ФИО, либо по employee_id
        employee = await client.api.dossier.get_employee(
            employee_fullname="Чурсанов Роман Евгеньевич"
        )
        print(f"Employee: {employee}")

        # Получить всех сотрудников
        all_employees = await client.api.dossier.get_employees()
        print(f"Employees list: {all_employees}")


if __name__ == "__main__":
    asyncio.run(main())
