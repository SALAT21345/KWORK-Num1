from aiogram import Dispatcher, types
import asyncio
import Handlers.MainHandler as MH
from CFG import bot 
from apscheduler.schedulers.asyncio import AsyncIOScheduler

async def set_commands(bot):
    commands = [
        types.BotCommand(command="start", description="Начать работу"),
        types.BotCommand(command="showrates", description="Подписки")  # Используйте строчные буквы
    ]
    await bot.set_my_commands(commands)

dp = Dispatcher()

async def main():
    dp.include_router(MH.router)
    scheduler = AsyncIOScheduler()
    scheduler.add_job(MH.CheckUserSub, "interval", hours=24, args=[bot])
    scheduler.add_job(MH.NotifyExpiringUsers, "interval", hours=24, args=[bot])
    scheduler.add_job(MH.CheckSubUserAndKickForGroup, "interval", hours=1, args=[bot])
    scheduler.start()
    await set_commands(bot)
    await dp.start_polling(bot)
if __name__ == '__main__':
    asyncio.run(main())

