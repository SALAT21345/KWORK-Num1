from aiogram import Dispatcher
import asyncio
import Handlers.MainHandler as MH
from CFG import bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler


dp = Dispatcher()

async def main():
    dp.include_router(MH.router)
    scheduler = AsyncIOScheduler()
    scheduler.add_job(MH.CheckUserSub, "interval", hours=24,args=[bot])
    scheduler.add_job(MH.NotifyExpiringUsers, "interval", hours=24, args=[bot])
    scheduler.start()
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
