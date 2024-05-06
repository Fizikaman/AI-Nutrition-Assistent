import logging
import os
from datetime import datetime

from aiogram.enums import ChatAction
from aiogram.filters import Command
from aiogram import Bot, Router, types, F
from openai import AsyncOpenAI

from chat_with_gpt import ans_from_gpt
import config
from process_text_message import process

router = Router(name=__name__)
logger = logging.getLogger(__name__)
client = AsyncOpenAI(api_key=config.CHAT_GPT_TOKEN)


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


@router.message(F.voice)
async def voice(message, bot: Bot):
    file_info = await bot.get_file(message.voice.file_id)
    downloaded_file = await bot.download_file(file_info.file_path)
    os.makedirs("/tmp", exist_ok=True)
    await message.bot.send_chat_action(
        chat_id=message.chat.id, action=ChatAction.RECORD_VOICE
    )
    try:
        response = await client.audio.transcriptions.create(
            file=("file.ogg", downloaded_file, "audio/ogg"),
            model="whisper-1",
        )
        ai_response = await process(response.text, message.from_user.id)
        ai_voice_response = await client.audio.speech.create(
            input=ai_response,
            voice="nova",
            model="tts-1-hd",
            response_format="opus",
        )
        with open("/tmp/ai_voice_response.ogg", "wb") as f:
            f.write(ai_voice_response.content)
    except Exception as e:
        await message.reply(f"Произошла ошибка, попробуйте позже!")
        return e

    await bot.send_voice(
        message.chat.id,
        voice=types.FSInputFile(os.path.join(config.BASE_DIR.parent, "/tmp/ai_voice_response.ogg")),
        reply_to_message_id=message.message_id,
    )

