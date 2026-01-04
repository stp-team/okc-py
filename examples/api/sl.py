import asyncio
import os

from dotenv import load_dotenv

from okc_py import OKC

load_dotenv()


async def main():
    async with OKC(
        username=os.getenv("OKC_USERNAME"), password=os.getenv("OKC_PASSWORD")
    ) as client:
        # Получаем фильтры для чатов (включает данные об очередях)
        filters = await client.api.sl.get_vq_chat_filter()
        print(f"Filters: {filters}")

        # Извлекаем список VQ из очередей
        queue_list = [vq for queue in filters.ntp_nck.queues for vq in queue.vqList]
        print(f"Number of queues: {len(queue_list)}")

        # Получаем SL данные за период
        # unit_id берется из filters.ntp_nck.unitId
        unit_id = filters.ntp_nck.unitId

        sl_data = await client.api.sl.get_sl(
            start_date="01.12.2025",
            stop_date="31.12.2025",
            units=unit_id,
            queues=queue_list,
        )

        print(f"SL data: {sl_data}")


if __name__ == "__main__":
    asyncio.run(main())
