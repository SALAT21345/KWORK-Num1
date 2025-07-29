from aiogram import Bot
from aiogram.enums.parse_mode import ParseMode
from aiogram.client.default import DefaultBotProperties
from dotenv import load_dotenv
import os

load_dotenv()  # Загружаем переменные окружения

token = os.getenv('BOT_TOKEN')
bot = Bot(token=token, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))
Start_Message = """Это сообщение можно менять через админ панель"""
InfoRatesMessage = """Тут вы можете приобрести нашу подписку по тарифам:
1 месяц / 2500 рублей
3 месяца / 6500 рублей (скидка 14%🔥)
6 месяцев / 12000 рублей (скидка 20%🔥)
12 месяцев / 24.000 ₽ (скидка 20%)
"""
channel_id = -4774948031
MESSAGE_TEMPLATES = {
    10: "🔔 До окончания вашей подписки осталось 10 дней. Не забудьте продлить её вовремя.",
    7:  "📅 Осталась неделя! Подписка истекает через 7 дней.",
    3:  "⏳ Ваша подписка истекает через 3 дня. Продление — это просто!",
    1:  "⚠️ Завтра закончится ваша подписка. Успейте продлить!",
    0:  "❌ Сегодня последний день действия вашей подписки.",
}
admin_id = 1243576393
AdminGroup = '-4846850110'