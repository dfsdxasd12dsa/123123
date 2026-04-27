import asyncio
import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

CONFIG_PATH = Path("bots.json")


@dataclass
class BotConfig:
    name: str
    token: str
    message_text: str
    button_text: str
    button_url: str


class ConfigStore:
    def __init__(self, config_path: Path):
        self.config_path = config_path
        self._mtime = 0.0
        self._configs: Dict[str, BotConfig] = {}

    def load_if_changed(self) -> None:
        if not self.config_path.exists():
            raise FileNotFoundError(
                f"Не найден файл {self.config_path}. Скопируйте bots.example.json в bots.json и заполните токены."
            )

        mtime = self.config_path.stat().st_mtime
        if mtime <= self._mtime and self._configs:
            return

        raw = json.loads(self.config_path.read_text(encoding="utf-8"))
        bots = raw.get("bots", [])

        configs: Dict[str, BotConfig] = {}
        for item in bots:
            cfg = BotConfig(
                name=item["name"],
                token=item["token"],
                message_text=item["message_text"],
                button_text=item["button_text"],
                button_url=item["button_url"],
            )
            configs[cfg.token] = cfg

        if not configs:
            raise ValueError("В bots.json нет ни одного бота в ключе 'bots'.")

        self._configs = configs
        self._mtime = mtime
        logging.info("Конфиг перезагружен: %s ботов", len(self._configs))

    def get(self, token: str) -> BotConfig:
        self.load_if_changed()
        if token not in self._configs:
            raise KeyError(
                "Для этого токена не найден конфиг. Добавьте бота в bots.json."
            )
        return self._configs[token]

    def tokens(self) -> List[str]:
        self.load_if_changed()
        return list(self._configs.keys())


store = ConfigStore(CONFIG_PATH)
dp = Dispatcher()


@dp.message(CommandStart())
async def on_start(message: Message, bot: Bot) -> None:
    cfg = store.get(bot.token)
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=cfg.button_text,
                    url=cfg.button_url,
                )
            ]
        ]
    )
    await message.answer(cfg.message_text, reply_markup=keyboard)


@dp.message(F.text == "/ping")
async def on_ping(message: Message) -> None:
    await message.answer("ok")


async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )

    tokens = store.tokens()
    bots = [Bot(token=token) for token in tokens]

    logging.info("Запускаю %s ботов", len(bots))
    await dp.start_polling(*bots)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Остановка")
