import asyncio

from okc_py import OKC


async def main():
    async with OKC(username="YOUR_USERNAME", password="YOUR_PASSWORD") as client:
        # Получить конкретного сотрудника. Поиск либо по ФИО, либо по employee_id
        employee = await client.dossier.get_employee(
            employee_fullname="Чурсанов Роман Евгеньевич"
        )
        print(f"Employee: {employee}")

        # Получить всех сотрудников
        all_employees = await client.dossier.get_employees()
        print(f"Employees list: {all_employees}")


if __name__ == "__main__":
    asyncio.run(main())
