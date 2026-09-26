import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import Message
from dotenv import load_dotenv

from gigachat_client import GigaChatClient
from style import StyleProfile

load_dotenv()

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("TG_BOT_TOKEN", "").strip()
if not BOT_TOKEN:
    raise SystemExit("Нет TG_BOT_TOKEN в .env")

ALLOWED_IDS = {
    int(x.strip())
    for x in os.getenv("ALLOWED_IDS", "").split(",")
    if x.strip().strip("-").isdigit()
}

router = Router()
giga = GigaChatClient()
profile = StyleProfile()

RATE_LIMIT_SECONDS = 1.5
PENDING = {}
ENABLED = {}


def is_owner(message: Message) -> bool:
    if not ALLOWED_IDS:
        return True
    return message.from_user.id in ALLOWED_IDS


async def delete_and_reply(message: Message, text: str):
    try:
        await message.delete()
    except Exception:
        pass
    await message.answer(text)


@router.message(F.text)
async def handle_message(message: Message):
    text = message.text.strip()
    low = text.lower()

    if low in (".startai", "ии включен", "ии включён"):
        if not is_owner(message):
            return
        ENABLED[message.chat.id] = True
        await delete_and_reply(message, "ИИ включен")
        return

    if low in (".stopai", "ии выключен", "ии выключён"):
        if not is_owner(message):
            return
        ENABLED[message.chat.id] = False
        await delete_and_reply(message, "ИИ выключен")
        return

    if not ENABLED.get(message.chat.id, False):
        return

    chat_id = message.chat.id
    now = asyncio.get_event_loop().time()
    last = PENDING.get(chat_id, 0)
    if now - last < RATE_LIMIT_SECONDS:
        await message.answer("....")
        return
    PENDING[chat_id] = now

    try:
        system = profile.build_system(add_user_name="ᴍᴀʜɪʀᴜ")
        user_text = profile.build_user(text)
        reply = await asyncio.to_thread(giga.chat, system, user_text)
        if not reply:
            reply = "...."
    except Exception as exc:
        logging.error("gigachat error: %s", exc)
        reply = "щас не могу, позже"

    await message.answer(reply[:4000])


async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())