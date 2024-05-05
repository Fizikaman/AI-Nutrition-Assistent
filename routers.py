import asyncio
import logging
from datetime import datetime

from aiogram.enums import ChatAction
from aiogram.filters import Command
from aiogram.utils.chat_action import ChatActionSender
from aiogram import Bot, Router, types, F

from chat_with_gpt import ans_from_gpt
import config

router = Router(name=__name__)
logger = logging.getLogger(__name__)


@router.message(F.text, Command("start"))
async def start(message: types.Message):
    await message.bot.send_chat_action(
        chat_id=message.chat.id, action=ChatAction.TYPING
    )
    username = message.from_user.username
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name

    if first_name is not None or last_name is not None:
        await message.answer(
            f"Привет, {'' if first_name is None else first_name} "
            f"{'' if last_name is None else last_name}❗"
        )
    else:
        await message.answer(f"Привет, {username}❗")

    await message.answer("Я твой умный ИИ-нутрициолог, который готов ответить на любые твои вопросы! "
                         "Как я могу помочь тебе?")


@router.message(F.text)
async def conversation_with_gpt(message: types.Message, bot: Bot):
    """Обработка старта"""
    await message.bot.send_chat_action(
        chat_id=message.chat.id, action=ChatAction.TYPING
    )
    logger.info(
        f"id: {message.from_user.id}, message: {message.text}, datetime: {datetime.now()}"
    )

    msg = await message.answer(
        "Дайте мне время подумать🤔. Среднее время ожидания 15-20 секунд."
    )
    await message.bot.send_chat_action(
        chat_id=message.chat.id, action=ChatAction.TYPING
    )
    response = await ans_from_gpt(message.from_user.id, message.text)
    await message.reply(response)
    await bot.delete_message(message.chat.id, msg.message_id)
