import asyncio
import logging

from openai import AsyncOpenAI
import config

# установка API ключа от CHAT_GPT
client = AsyncOpenAI(api_key=config.CHAT_GPT_TOKEN)
memory = config.MEMORY_DICT  # словарь для хранения ответов
logger = logging.getLogger(__name__)


async def ans_from_gpt(user_id, prompt):
    """Функция для взаимодействия с openai через API"""
    # проверка пользователя по id_tg и запись вопроса пользователя
    if user_id not in memory:
        memory[user_id] = []
        memory[user_id].append({"role": "user", "content": prompt})

    else:
        memory[user_id].append({"role": "user", "content": prompt})

    thread = await client.beta.threads.create(messages=memory[user_id])

    #  запуск нового потока и отправка ассистенту
    run = await client.beta.threads.runs.create(
        thread_id=thread.id, assistant_id=config.ASS_ID
    )

    while True:
        run = await client.beta.threads.runs.retrieve(
            thread_id=thread.id, run_id=run.id
        )

        if run.status == "completed":
            logger.info("done")
            message_response = await client.beta.threads.messages.list(
                thread_id=thread.id
            )
            messages = message_response.data
            latest_message = messages[0]
            answer = latest_message.content[0].text.value
            memory[user_id].append({"role": "user", "content": answer})
            break

        else:
            await asyncio.sleep(3)

    # очистка списка по одной паре вопрос/ответ
    if len(memory[user_id]) > 12:
        del memory[user_id][0:2]

    return answer