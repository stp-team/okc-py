import asyncio

from src.okc_py import Client
from src.okc_py.config import Settings


async def main():
    async with Client(
        settings=Settings(
            BASE_URL="https://okc.ertelecom.ru/yii",
            USERNAME="grigorev.is2",
            PASSWORD="Grigorev1230033ISSSS1!",
        )
    ) as client:
        response = await client.tests.get_categories()
        print(response)


if __name__ == "__main__":
    asyncio.run(main())
