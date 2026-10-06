import asyncio
import os
from funstat import FunstatClient

async def main():
    base_url = os.environ.get("FUNSTAT_BASE_URL")
    token = os.environ.get("FUNSTAT_TOKEN")

    async with FunstatClient(base_url, token) as api:
        print("Bot Railway'da muvaffaqiyatli ishga tushdi!")
        while True:
            await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(main())
