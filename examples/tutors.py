import asyncio

from okc_py import OKC


async def main():
    async with OKC(username="YOUR_USERNAME", password="YOUR_PASSWORD") as client:
        graph_filters = await client.tutors.get_graph_filters(division_id=2)

        tutor_graph = await client.tutors.get_full_graph(
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
        print(tutor_graph)


if __name__ == "__main__":
    asyncio.run(main())
