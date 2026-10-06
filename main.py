import sys
import os
import asyncio

# Указываем Python искать модули в папке src
sys.path.append("src")

from funstat import FunstatClient

async def main():
    # Получаем настройки из Variables в Railway
    base_url = os.environ.get("FUNSTAT_BASE_URL")
    token = os.environ.get("FUNSTAT_TOKEN")

    if not token or not base_url:
        print("ОШИБКА: Переменные FUNSTAT_TOKEN или FUNSTAT_BASE_URL не заданы в Railway Variables!")
        return

    print("Подключение к Funstat API...")
    
    async with FunstatClient(base_url, token) as api:
        print("Бот успешно запущен и работает 24/7!")
        
        # Бесконечный цикл, чтобы сервис на Railway не отключался
        while True:
            await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(main())

