import asyncio

from okc_py import OKC


async def main():
    async with OKC(username="YOUR_USERNAME", password="YOUR_PASSWORD") as client:
        employee = await client.dossier.get_employee(
            employee_fullname="Чурсанов Роман Евгеньевич"
        )
        print(employee)


if __name__ == "__main__":
    asyncio.run(main())
