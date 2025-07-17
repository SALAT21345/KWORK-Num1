from aiogram import Dispatcher
import asyncio
import Handlers.MainHandler as MH
from CFG import bot

# ⛔️ Ошибка была тут: dp = Dispatcher — ты просто присваивал класс, а не создавал экземпляр
dp = Dispatcher()  # ✅ Правильно: создаем объект Dispatcher

async def main():
    dp.include_router(MH.router)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
