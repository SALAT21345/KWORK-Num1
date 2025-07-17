from aiogram.filters import CommandStart,Command
from aiogram.fsm.context import FSMContext
from aiogram import Router,F
from aiogram.types import Message, CallbackQuery
from aiogram import types 
from aiogram.enums.parse_mode import ParseMode

router = Router()
@router.message(CommandStart())
async def Start(message: Message):
    await message.answer("ТЕСТ")