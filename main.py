import sys
import os
import subprocess
import asyncio

# 1. Zaruriy kutubxonalarni avtomatik tekshirish va o'rnatish
def install_dependencies():
    required = ["httpx", "pydantic"]
    for package in required:
        try:
            __import__(package)
        except ImportError:
            print(f"{package} topilmadi, o'rnatilmoqda...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])

install_dependencies()

# 2. Python yo'llariga src papkasini qo'shish
sys.path.append("src")
sys.path.append(".")

# 3. Endi bemalol import qilamiz
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


