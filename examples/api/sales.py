import asyncio
import os

from dotenv import load_dotenv

from okc_py import OKC

load_dotenv()


async def main():
    async with OKC(
        username=os.getenv("OKC_USERNAME"), password=os.getenv("OKC_PASSWORD")
    ) as client:
        filters = await client.api.sales.get_filters()
        print(f"Filters: {filters}")

        filters_by_date = await client.api.sales.get_filters_by_date(
            "1.12.2025", "1.1.2026"
        )
        for head in filters_by_date.heads:
            print(
                f"{head.employee_fullname} - Unit: {head.unit_id},"
                f" Subdivision: {head.subdivision_id}"
            )
        for emp in filters_by_date.employees:
            print(
                f"{emp.employee_fullname} - Head: {emp.head_id}, Active to: {emp.active_to}"
            )

        sales = await client.api.sales.get_report(
            sales_types=["SaleMaterialsEns", "SaleTestDrive", "SalePPDRequests"],
            units=[7],
            start_date="01.12.2025",
            stop_date="05.01.2026",
        )

        for sale in sales.data:
            print(
                f"{sale.employee_fullname} ({sale.unit_name}):"
                f" {sale.materials_ens_name} in {sale.cost_type}"
                f" at {sale.sale_date} with base cost {sale.base_cost}Р"
            )


if __name__ == "__main__":
    asyncio.run(main())
