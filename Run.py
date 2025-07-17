from aiogram import Dispatcher 
import asyncio
import Handlers.MainHandler as MH
from CFG import bot
dp = Dispatcher

async def main():
    dp.include_routers(MH.router)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())