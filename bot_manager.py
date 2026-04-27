import asyncio
import logging
from pathlib import Path

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

TOKENS_FILE = Path("tokens.txt")
MESSAGE_FILE = Path("message.txt")
BUTTON_URL_FILE = Path("button_url.txt")
BUTTON_TEXT_FILE = Path("button_text.txt")

DEFAULT_MESSAGE = "👋 Добро пожаловать!\n\n👇 Перейдите по кнопке ниже."
DEFAULT_BUTTON_TEXT = "Перейти"


def ensure_files() -> None:
    if not TOKENS_FILE.exists():
        TOKENS_FILE.write_text(
            "# Вставь токены сюда, 1 токен = 1 строка\n"
            "# 123456:ABC_TOKEN\n",
            encoding="utf-8",
        )

    if not MESSAGE_FILE.exists():
        MESSAGE_FILE.write_text(DEFAULT_MESSAGE, encoding="utf-8")

    if not BUTTON_URL_FILE.exists():
        BUTTON_URL_FILE.write_text("", encoding="utf-8")

    if not BUTTON_TEXT_FILE.exists():
        BUTTON_TEXT_FILE.write_text(DEFAULT_BUTTON_TEXT, encoding="utf-8")


def read_tokens() -> list[str]:
    tokens = [
        line.strip()
        for line in TOKENS_FILE.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]
    if not tokens:
        raise ValueError(
            "Файл tokens.txt пустой. Добавь токены (1 токен = 1 строка) и запусти снова."
        )
    return tokens


def read_message() -> str:
    text = MESSAGE_FILE.read_text(encoding="utf-8").strip()
    return text or DEFAULT_MESSAGE


def read_button_url() -> str:
    return BUTTON_URL_FILE.read_text(encoding="utf-8").strip()


def read_button_text() -> str:
    text = BUTTON_TEXT_FILE.read_text(encoding="utf-8").strip()
    return text or DEFAULT_BUTTON_TEXT


dp = Dispatcher()


@dp.message(CommandStart())
async def on_start(message: Message) -> None:
    message_text = read_message()
    button_url = read_button_url()
    button_text = read_button_text()

    if button_url:
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text=button_text, url=button_url)]]
        )
        await message.answer(message_text, reply_markup=keyboard)
    else:
        await message.answer(message_text)


@dp.message(F.text == "/ping")
async def on_ping(message: Message) -> None:
    await message.answer("ok")


async def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
    ensure_files()

    tokens = read_tokens()
    bots = [Bot(token=t) for t in tokens]

    logging.info("Запускаю %s ботов", len(bots))
    await dp.start_polling(*bots)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Остановка")
