from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# Выбор тарифа
Btn_rate_One = InlineKeyboardButton(text='Тариф 1', callback_data='Rate_1')
Btn_rate_Two = InlineKeyboardButton(text='Тариф 2', callback_data='Rate_2')
Btn_rate_Free = InlineKeyboardButton(text='Тариф 3', callback_data='Rate_3')

# Инфо кнопки
Btn_Helper = InlineKeyboardButton(text='Тех.Поддержка', callback_data='GetHelp')
Btn_Chat = InlineKeyboardButton(text='Наш чат',callback_data='GetChat')
SelectRate = InlineKeyboardMarkup(inline_keyboard=[
    [Btn_rate_One,
    Btn_rate_Two,
    Btn_rate_Free],
    [Btn_Helper,Btn_Chat]
])