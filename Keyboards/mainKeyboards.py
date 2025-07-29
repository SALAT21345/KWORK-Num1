from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# Выбор тарифа
Btn_rate_One = InlineKeyboardButton(text='1 месяц', callback_data='Rate_1')
Btn_rate_Two = InlineKeyboardButton(text='3 месяца', callback_data='Rate_2')
Btn_rate_Free = InlineKeyboardButton(text='6 месяцев', callback_data='Rate_3')
Btn_rate_five = InlineKeyboardButton(text='12 месяцев', callback_data='Rate_4')

# Инфо кнопки
Btn_GoMiling = InlineKeyboardButton(text='Да, начать рассылку', callback_data='GoMiling')
Btn_StopMiling = InlineKeyboardButton(text="Изменить сообщение", callback_data='StopMiling')
BtnShowGroup = InlineKeyboardButton(text='Наше сообщество',url='https://t.me/+DJfn6NyHmRAzMTdi')
BtnShowRates = InlineKeyboardButton(text='Подписаться на контент', callback_data='ShowRates')
Btn_Helper = InlineKeyboardButton(text='Тех. поддержка', url='https://t.me/admrekontent')
Btn_Chat = InlineKeyboardButton(text='Наш чат',callback_data='GetChat')

SelectRates = InlineKeyboardMarkup(inline_keyboard=[
    [Btn_rate_One,Btn_rate_Two,Btn_rate_Free]
])



StartBtns = InlineKeyboardMarkup(inline_keyboard=[
    [BtnShowRates],
    [BtnShowGroup],
    [Btn_Helper]
    ])

BtnMiling = InlineKeyboardMarkup(inline_keyboard=[
    [Btn_GoMiling, Btn_StopMiling]
])

def generate_edit_posts_kb(posts):
    buttons = []
    for post in posts:
        btn = InlineKeyboardButton(
            text=f"Пост от {post['date'][:10]}",
            callback_data=f"edit_post_{post['message_id']}"
        )
        buttons.append([btn])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

