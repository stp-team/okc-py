import asyncio
import os

from dotenv import load_dotenv

from okc_py import OKC

load_dotenv()


async def main():
    async with OKC(
        username=os.getenv("OKC_USERNAME"), password=os.getenv("OKC_PASSWORD")
    ) as client:
        # Получить доступные фильтры (для автоматического заполнения следующего запроса
        graph_filters = await client.api.tutors.get_filters(division_id=2)
        print(f"Graph filters: {graph_filters}")

        # Получить график наставников за промежуток времени
        tutor_graph = await client.api.tutors.get_full_graph(
            division_id=2,
            start_date="1.12.2025",
            stop_date="1.1.2026",
            picked_units=[unit.id for unit in graph_filters.units],
            picked_tutor_types=[
                tutor_type.id for tutor_type in graph_filters.tutor_types
            ],
            picked_shift_types=[
                shift_type.id for shift_type in graph_filters.shift_types
            ],
        )
        print(f"Tutors schedule: {tutor_graph}")


if __name__ == "__main__":
    asyncio.run(main())
