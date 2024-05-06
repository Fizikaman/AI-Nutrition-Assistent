import base64
import logging

from openai import AsyncOpenAI

import config

memory = config.MEMORY_DICT
client = AsyncOpenAI(api_key=config.CHAT_GPT_TOKEN)
logger = logging.getLogger(__name__)


async def process(prompt, user_id, image_content=None) -> str:
    model = "gpt-3.5-turbo"
    max_tokens = None
    logger.info(f"User_id: {user_id}.")

    if user_id not in memory:
        memory[user_id] = []
        memory[user_id].append({"role": "user", "content": prompt})
    else:
        memory[user_id].append({"role": "user", "content": prompt})

    if image_content is not None:
        model = "gpt-4-vision-preview"
        max_tokens = 4000
        base64_image_content = base64.b64encode(image_content).decode("utf-8")
        base64_image_content = f"data:image/jpeg;base64,{base64_image_content}"
        memory[user_id].append(
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": base64_image_content}},
                ],
            }
        )

    try:
        chat_completion = await client.chat.completions.create(  # Ожидаем завершения корутины
            model=model, messages=memory[user_id], max_tokens=max_tokens
        )
        ai_response = chat_completion.choices[0].message.content
        memory[user_id].append({"role": "assistant", "content": ai_response})
        return ai_response
    except Exception as e:
        if type(e).__name__ == "BadRequestError":
            del memory[user_id]
        else:
            raise e
        logger.info(f"Error: {e}.")
