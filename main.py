import sys
import os
import asyncio

# 1. Avval Python yo'llariga src va joriy papkani qo'shamiz
sys.path.append("src")
sys.path.append(".")

# 2. Keyin httpx va funstat modulini import qilamiz
import httpx
from funstat import FunstatClient

async def main():
    base_url = os.environ.get("FUNSTAT_BASE_URL")
    funstat_token = os.environ.get("FUNSTAT_TOKEN")

    if not funstat_token or not base_url:
        print("XATOLIK: FUNSTAT_TOKEN yoki FUNSTAT_BASE_URL Variables'ga kiritilmagan!")
        return

    print("Funstat API'ga ulanish...")
    
    async with FunstatClient(base_url, funstat_token) as api:
        print("Bot Railway'da muvaffaqiyatli ishga tushdi va ishlayapti!")
        while True:
            await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(main())


