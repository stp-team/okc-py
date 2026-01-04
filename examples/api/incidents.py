import asyncio
import os

from dotenv import load_dotenv

from okc_py import OKC

load_dotenv()


async def main():
    async with OKC(
        username=os.getenv("OKC_USERNAME"), password=os.getenv("OKC_PASSWORD")
    ) as client:
        filters = await client.api.incidents.get_filters()
        print(f"Filters: {filters}")

        incidents = await client.api.incidents.get_incidents(
            start_date="01.12.2025",
            stop_date="01.01.2026",
        )
        for incident in incidents:
            print(
                f"{incident.scale} - {incident.start_date}: {incident.product} - {incident.description[:50]}..."
            )


if __name__ == "__main__":
    asyncio.run(main())
