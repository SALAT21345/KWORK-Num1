from aiogram.filters import CommandStart,Command
from aiogram.fsm.context import FSMContext
from aiogram import Router,F
from aiogram.types import Message, CallbackQuery
from aiogram import types
from aiogram.fsm.state import StatesGroup,State
from aiogram.types import LabeledPrice,ChatInviteLink
from calendar import monthrange
from CFG import Bot
from Keyboards.mainKeyboards import StartBtns,SelectRates,BtnMiling
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime,timezone
from aiogram.exceptions import TelegramBadRequest
import BdController as BD
import sqlite3
router = Router()
TextForMiling = ""
import CFG as CFG

POST_DB = []

class ChangeStartText(StatesGroup):
    GetText = State()

class ChangeTextOfRates(StatesGroup):
    GetText = State()

class CreateNewPostState(StatesGroup):
    GetText = State()

class CreateMailing(StatesGroup):
    GetText = State()

class EditPostState(StatesGroup):
    waiting_for_new_text = State()
    message_id = State()

@router.message(CommandStart())
async def Start(message: Message):
    if message.chat.type == "private":
        await message.answer(f"{CFG.Start_Message}", reply_markup=StartBtns)
        BD.InitNotificationTable()
        BD.inicialize_Users(message.chat.id,f"{message.from_user.username}")
        print(BD.CheckUser(1243576393))
    else:
        # await message.answer('Вы в группе или беседе')
        pass



@router.message(Command('ShowRates'))
@router.callback_query(F.data == 'ShowRates')
async def ShowRates(callback:CallbackQuery):
    await callback.message.answer(f'{CFG.InfoRatesMessage}',reply_markup=SelectRates)

async def CheckSubUserAndKickForGroup(bot: Bot):
    allUsers = BD.GetAllUsers()
    for user in allUsers:
        user_id = user[0]
        end_sub_str = user[3]

        # Пропускаем, если нет даты окончания
        if not end_sub_str:
            continue

        # Преобразуем дату из строки в datetime
        try:
            end_sub = datetime.strptime(end_sub_str, "%Y-%m-%d")
        except ValueError:
            continue  # если неверный формат даты — пропускаем

        # Если подписка еще активна — пропускаем
        if end_sub.date() >= datetime.now().date():
            continue

        # Получаем статус пользователя в группе
        try:
            member = await bot.get_chat_member(chat_id=-1002899688608, user_id=user_id)
        except Exception as e:
            print(f"Ошибка получения статуса пользователя {user_id}: {e}")
            continue

        # Пропускаем владельцев и админов
        if member.status in ("creator", "administrator"):
            continue

        # Кикаем: ban + unban, чтобы мог вернуться при новой подписке
        try:
            await bot.ban_chat_member(chat_id=-1002899688608, user_id=user_id)
            await bot.unban_chat_member(chat_id=-1002899688608, user_id=user_id)
        except Exception as e:
            print(f"Ошибка при удалении пользователя {user_id}: {e}")



# Admin Commands

def generate_edit_posts_kb(posts):
    buttons = []
    for post in posts:
        btn = InlineKeyboardButton(
            text=f"Пост от {post['date'].strftime('%d.%m.%Y')}",
            callback_data=f"edit_post_{post['message_id']}"
        )
        buttons.append([btn])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

@router.message(Command('AdminMenu'))
async def StartAdminMenu(message:Message):
    if message.from_user.id == CFG.admin_id:
        await message.answer("--==AdminMenu==--\n<b>Список админ-команд</b>\n\n/ChangeStartMessages - <b>Изменить текст приветственного сообщения.</b>\n/CreateNewPost - <b>Опубликовать новый пост</b>\n/EditPost - <b>Редактировать последние 3 поста.</b>\n/GetAllUsers - <b>Получить данные всех пользователей</b>\n/ChangeMessageOfRates - <b>Изменить текст сообщения после нажатия на кнопку 'Подписаться на контент'</b>\n\nНапоминания.\n/show_notifications - Показать установленные напоминания\n/set_notice (days) (message)- установить напоминение на кол-во дней до окончания подписки.\n/delete_notification (дней) - удалить напоминание за какое то кол-во дней до окончания подписки",parse_mode="HTML")
    else:
        await message.answer("У вас нет доступа к админ панеле.")


@router.message(Command("EditPost"))
async def list_last_posts(message: Message):
    posts = BD.Get_Posts_From_Start_Of_Month()
    posts = sorted(posts, key=lambda x: x["date"], reverse=True)[:5]

    if not posts:
        await message.answer("Нет постов для редактирования.")
        return

    kb = generate_edit_posts_kb(posts)
    await message.answer("Выберите пост для редактирования:", reply_markup=kb)

@router.callback_query(F.data.startswith("edit_post_"))
async def start_post_edit(callback: CallbackQuery, state: FSMContext):
    message_id = int(callback.data.split("_")[-1])
    await state.set_state(EditPostState.waiting_for_new_text)
    await state.update_data(message_id=message_id)

    await callback.message.answer("Введите новый текст для поста.")


@router.message(EditPostState.waiting_for_new_text)
async def apply_post_edit(message: Message, state: FSMContext):
    data = await state.get_data()
    message_id = data["message_id"]

    try:
        await message.bot.edit_message_text(
            chat_id=CFG.channel_id,   # укажи здесь свой канал
            message_id=message_id,
            text=message.text
        )
        await message.answer("✅ Пост успешно отредактирован.")
    except Exception as e:
        await message.answer(f"❌ Ошибка при редактировании поста: {e}", parse_mode=None)

    await state.clear()


async def NotifyExpiringUsers(bot: Bot):
    for days in [10, 7, 3, 1]:  # дни, за которые нужно отправить уведомления
        users = BD.GetUsersWithExpiringSubscription(days_before=days)  # получаем пользователей
        message = BD.GetNotificationMessage(days)  # получаем сообщение из БД

        if not message or not users:
            continue  # если нет ни сообщений, ни пользователей — пропускаем

        for user_id in users:
            try:
                await bot.send_message(chat_id=user_id, text=message, parse_mode="HTML")
            except Exception as e:
                print(f"❌ Не удалось отправить сообщение {user_id}: {e}")

@router.message(Command("set_notice"))
async def set_notification_message(msg: types.Message):
    # Пример команды: /set_notice 3 Ваша подписка истекает через 3 дня!
    parts = msg.text.split(maxsplit=2)
    if len(parts) < 3 or not parts[1].isdigit():
        await msg.reply("⚠️ Формат команды: /set_notice (дней) (сообщение)", parse_mode='HTML')
        return

    days = int(parts[1])
    message = parts[2]

    if BD.SetNotificationMessage(days, message):
        await msg.reply(f"✅ Сообщение на {days} дней до окончания подписки обновлено.")
    else:
        await msg.reply("❌ Не удалось сохранить сообщение.")



@router.message(Command('delete_notification'))
async def delete_notification_handler(message: Message):
    if message.from_user.id != CFG.admin_id:
        await message.answer("У вас нет доступа к этой команде.")
        return

    args = message.text.split()
    if len(args) != 2 or not args[1].isdigit():
        await message.answer("Использование команды: /delete_notification <число_дней>")
        return

    days_before = int(args[1])
    success = BD.DeleteNotificationMessage(days_before)
    if success:
        await message.answer(f"Уведомление за {days_before} дней успешно удалено.")
    else:
        await message.answer(f"Уведомление за {days_before} дней не найдено.")

@router.message(Command('show_notifications'))
async def show_notifications_handler(message: Message):
    if message.from_user.id != CFG.admin_id:
        await message.answer("У вас нет доступа к этой команде.")
        return

    notifications = BD.GetAllNotificationMessages()
    if not notifications:
        await message.answer("Сообщения для уведомлений не установлены.")
        return

    text = "Установленные уведомления:\n\n"
    for row in notifications:
        days_before, msg = row
        text += f"За {days_before} дней до окончания подписки:\n{msg}\n\n"

    await message.answer(text)


@router.message(Command('CreateNewPost'))
async def CreateNewPostGetText(message:Message,state:FSMContext):
    if message.from_user.id == CFG.admin_id:
        await message.answer("Отправьте пост для публикации в канал")
        await state.set_state(CreateNewPostState.GetText)
    else:
        await message.answer("У вас нет доступа к админ панеле.")




@router.message(CreateNewPostState.GetText)
async def CreateNewPost(message: Message, state: FSMContext):
    caption = message.caption or message.text or ""
    file_id = None

    if message.photo:
        file_id = message.photo[-1].file_id  # самое большое фото
        msg = await post_photo_to_channel(message.bot, -1002899688608, file_id, caption, message.from_user.id)
        if msg is None:
            return  #
    elif message.video:  # проверка на наличие видео
        file_id = message.video.file_id
        msg = await message.bot.send_video(chat_id=-1002899688608, video=file_id, caption=caption)
    else:
        msg = await message.bot.send_message(chat_id=-1002899688608, text=caption)

    raw_date = str(msg.date)
    dt = datetime.fromisoformat(raw_date)
    formatted = dt.strftime("%Y-%m-%d %H:%M:%S")
    BD.SaveNewPost(formatted, msg.message_id)

    await message.answer("✅ Пост опубликован.")
    await state.clear()

async def post_photo_to_channel(bot: Bot, chat_id: int, file_id: str, caption: str, user_id: int) -> Message:
    if len(caption) > 1024:
        await bot.send_message(user_id, "❌ Ошибка: описание слишком длинное. Максимум 1024 символа.")
        return None

    return await bot.send_photo(
        chat_id=chat_id,
        photo=file_id,
        caption=caption
    )

@router.message(Command("ChangeMessageOfRates"))
async def ChangeMessageOfRates(message:Message,state:FSMContext):
    if message.from_user.id == CFG.admin_id:
        await message.answer("Напишите следующим сообщением текст которое будет показываться после нажатия кнопки 'Подписаться на контент'")
        await state.set_state(ChangeTextOfRates.GetText)
    else:
        await message.answer("У вас нет доступа к админ панеле.")


@router.message(ChangeTextOfRates.GetText)
async def ChangeTextOfRatesSetText(message:Message,state:FSMContext):
    TextOfRates = message.text
    CFG.InfoRatesMessage = TextOfRates
    await state.clear()
    await message.answer(f"Текстовое сообщение после нажатия на 'Подписаться на контент' теперь:\n\n{CFG.InfoRatesMessage}")

@router.message(Command('ChangeStartMessages'))
async def ChangeStartMessagesStart(message:Message, state: FSMContext):
    if message.from_user.id == CFG.admin_id:
        await message.answer("Напишите следующим сообщением текст который вы хотите видеть при команде /start")
        await state.set_state(ChangeStartText.GetText)
    else:
        await message.answer("У вас нет доступа к админ панеле.")

@router.message(ChangeStartText.GetText)
async def ChangeStartMessagesGetText(message:Message, state:FSMContext):
    StartText = message.text
    CFG.Start_Message = StartText
    await state.clear()
    await message.answer("Супер! Теперь текстовое сообщение на команду '/start'\n\n"+CFG.Start_Message)


@router.message(Command('GetAllUsers'))
async def GetAllUser(message:Message):
    if message.chat.id == CFG.admin_id:
        result = BD.GetAllUsers()
        AllUsersInfo = ""
        if result:
            for i, user in enumerate(result, start=1):
                TempInfo = f'Пользователь №{i}\nUser ID: {user[0]}\nПрофиль: <a href="https://t.me/{user[4]}">Ckick</a>\nПодписка: {'YES' if user[1] else 'NO'}\nДата оплаты подписки: {user[2]}\nДата окончания подписки: {user[3]}'
                AllUsersInfo += TempInfo + "\n\n"
        else:
            AllUsersInfo = "Нет пользователей в базе данных."

        await message.answer(AllUsersInfo,parse_mode="HTML",disable_web_page_preview=True)
    else:
        await message.answer("У вас нет доступа к админ панеле.")



@router.message(Command('mailing'))                     # Рассылка
async def mailingCommand(message:Message,state:FSMContext):
    if message.chat.id == CFG.admin_id:
        await message.answer("Отправьте сообщение для рассылки")
        await state.set_state(CreateMailing.GetText)
    else:
        await message.answer("У вас нет доступа к админ панеле.")

@router.callback_query(F.data =='StopMiling')
async def mailing(callback:CallbackQuery,state:FSMContext):
    if callback.message.chat.id == CFG.admin_id:
        await callback.message.answer("Отправьте сообщение для рассылки")
        await state.set_state(CreateMailing.GetText)

@router.message(CreateMailing.GetText)
async def Mailing_Accept(message: Message, state: FSMContext):
    TextForMiling = message.text
    await state.update_data(TextForMiling=TextForMiling)
    await message.answer(f'Начать рассылку сообщения:\n\n{TextForMiling}', reply_markup=BtnMiling)

@router.callback_query(F.data == 'GoMiling')
async def GoMailing(callback: CallbackQuery, bot: Bot, state: FSMContext):
    data = await state.get_data()
    text = data.get("TextForMiling", "Сообщение не найдено.")
    Users = BD.GetAllUsers()
    for i, user in enumerate(Users, start=0):
        await bot.send_message(chat_id=user[0], text=text)
    await callback.message.answer("Рассылка успешно завершена!")
    await state.clear()







@router.callback_query(F.data == 'Rate_1')          # CallBack Начало подписок
@router.callback_query(F.data == 'Rate_2')
@router.callback_query(F.data == 'Rate_3')
@router.callback_query(F.data == 'Rate_4')
async def Payment(callback: CallbackQuery, bot: Bot):
    price = 2500
    rate = callback.data
    Rate = 0
    tariff = rate.split('_')[1]

    if tariff == "1":
        price = 250000
        title = 'Тариф на 1 месяц'
        Rate = 1
    elif tariff == "2":
        price = 650000
        title = 'Тариф на 3 месяца'
        Rate = 3
    elif tariff == "3":
        price = 1200000
        title = 'Тариф на 6 месяцев'
        Rate = 6
    elif tariff == "4":
        price = 2400000
        title = 'Тариф на 12 месяцев'
        Rate = 12
    else:
        await callback.message.answer("Неизвестный тариф")
        return

    prices = [LabeledPrice(label='Подписка', amount=price)]

    await bot.send_invoice(
        chat_id=callback.message.chat.id,
        title=title,
        description="Оплата подписки на контент",
        payload=str(Rate),
        provider_token="381764678:TEST:133159",
        currency="RUB",
        prices=prices,
        start_parameter="test-invoice",
        need_email=False
    )

@router.pre_checkout_query()
async def pre_checkout(pre_checkout_q: types.PreCheckoutQuery, bot:Bot):
    await bot.answer_pre_checkout_query(pre_checkout_q.id, ok=True)

@router.message(F.successful_payment)
async def successful_payment(message: Message,bot:Bot):
    payment_info = message.successful_payment

    total_amount = payment_info.total_amount  # сумма в копейках
    currency = payment_info.currency
    payload = payment_info.invoice_payload

    # Переводим в рубли
    amount_rub = total_amount / 100

    await message.answer(
        f"✅ Оплата прошла успешно!\n"
        f"Сумма: {amount_rub:.2f} {currency}\n"
        f"Тариф: {payload} месяц(ев)"
    )
    BD.AddSubUser(message.from_user.id, int(payload))
    await create_invite(message=message, bot=message.bot)
    await message.answer("Ниже будут посты, уже вышедшие в этом месяце. Весь остальной контент будет ждать вас ежедневно в нашей закрытой группе 🧡")
    await get_my_posts(message=message, bot=message.bot)
    await PostMessageForNewSub(User_id=message.chat.id,bot=bot)

                                                                                # Functions


async def create_invite(message, bot):
    try:
        chat_id = -1002899688608

        invite_link: ChatInviteLink = await bot.create_chat_invite_link(
            chat_id=chat_id,
            expire_date=None,
            member_limit=1,
            creates_join_request=False
        )

        await message.answer(f"Вот твоя персональная ссылка на вступление в группу:\n{invite_link.invite_link}",parse_mode=None)

    except Exception as e:
        await message.answer(f"Ошибка при создании ссылки: {e}")

async def get_my_posts(message, bot):
    posts = BD.Get_Posts_From_Start_Of_Month()
    for post in posts:
        try:
            await bot.copy_message(
                chat_id=message.chat.id,
                from_chat_id=post["channel_id"],
                message_id=post["message_id"]
            )
        except TelegramBadRequest as e:
            if "message to copy not found" in str(e):
                # Сообщение удалено или недоступно — пропускаем этот пост
                print(f"Пропускаю пост message_id={post['message_id']} — сообщение не найдено")
                continue
            else:
                # Если другая ошибка — выбрасываем дальше
                raise
        except Exception as e:
            # Можно добавить логирование или обработку других исключений
            print(f"Ошибка при копировании сообщения {post['message_id']}: {e}")

async def post_to_channel(bot,ChanelID,text):
    msg = await bot.send_message(chat_id=ChanelID,text=text)
    raw_date = str(msg.date)
    dt = datetime.fromisoformat(raw_date)
    formatted = dt.strftime("%Y-%m-%d %H:%M:%S")
    BD.SaveNewPost(formatted,msg.message_id)
    print(formatted)


async def PostMessageForNewSub(User_id,bot):
    UserInfo = BD.CheckUser(User_id)
    Info = f"<a href='https://t.me/{UserInfo[2]}'>Пользователь</a> оплатил подписку на: {UserInfo[0]} месяц(ев)."
    await bot.send_message(chat_id=CFG.AdminGroup,text=Info,parse_mode="HTML")

async def CheckUserSub(bot: Bot):
    expired_users = BD.RemoveExpiredSubscriptions()

    if not expired_users:
        print("Нет пользователей с истёкшей подпиской.")
        return

    for user_id in expired_users:
        try:
            await bot.send_message(
                chat_id=int(user_id),
                text="📛 Ваша подписка истекла.\nЧтобы снова получить доступ, пожалуйста, оформите новую подписку.",
                parse_mode="HTML"
            )
            print(f"Отправлено уведомление пользователю {user_id}")
        except Exception as e:
            print(f"❌ Не удалось отправить сообщение пользователю {user_id}: {e}")
