import asyncio
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import List

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

TOKENS_PATH = Path("tokens.txt")
MESSAGE_PATH = Path("message.txt")
BUTTON_TEXT_PATH = Path("button_text.txt")
BUTTON_URL_PATH = Path("button_url.txt")


@dataclass
class RuntimeConfig:
    tokens: List[str]
    message_text: str
    button_text: str
    button_url: str


class FileConfigStore:
    def __init__(
        self,
        tokens_path: Path,
        message_path: Path,
        button_text_path: Path,
        button_url_path: Path,
    ):
        self.tokens_path = tokens_path
        self.message_path = message_path
        self.button_text_path = button_text_path
        self.button_url_path = button_url_path
        self._mtimes = {}
        self._config: RuntimeConfig | None = None

    def _read_tokens(self) -> List[str]:
        if not self.tokens_path.exists():
            raise FileNotFoundError(
                f"Не найден файл {self.tokens_path}. Создайте его и добавьте токены (каждый токен с новой строки)."
            )

        tokens = [
            line.strip()
            for line in self.tokens_path.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.strip().startswith("#")
        ]

        if not tokens:
            raise ValueError("Файл tokens.txt пустой. Добавьте хотя бы 1 токен.")

        return tokens

    def _read_text_file(self, path: Path, *, default: str = "") -> str:
        if not path.exists():
            return default
        return path.read_text(encoding="utf-8").strip()

    def _is_changed(self) -> bool:
        files = [
            self.tokens_path,
            self.message_path,
            self.button_text_path,
            self.button_url_path,
        ]

        for file in files:
            current_mtime = file.stat().st_mtime if file.exists() else -1.0
            if self._mtimes.get(file) != current_mtime:
                return True

        return self._config is None

    def load_if_changed(self) -> None:
        if not self._is_changed():
            return

        tokens = self._read_tokens()
        message_text = self._read_text_file(self.message_path)
        if not message_text:
            raise ValueError(
                "Файл message.txt пустой или отсутствует. Добавьте текст, который будет отправляться на /start."
            )

        button_text = self._read_text_file(self.button_text_path, default="Перейти")
        button_url = self._read_text_file(self.button_url_path)

        self._config = RuntimeConfig(
            tokens=tokens,
            message_text=message_text,
            button_text=button_text,
            button_url=button_url,
        )

        for file in [
            self.tokens_path,
            self.message_path,
            self.button_text_path,
            self.button_url_path,
        ]:
            self._mtimes[file] = file.stat().st_mtime if file.exists() else -1.0

        logging.info("Конфиг перезагружен: %s токенов", len(tokens))

    def get(self) -> RuntimeConfig:
        self.load_if_changed()
        if self._config is None:
            raise RuntimeError("Конфиг не загружен")
        return self._config


store = FileConfigStore(
    TOKENS_PATH,
    MESSAGE_PATH,
    BUTTON_TEXT_PATH,
    BUTTON_URL_PATH,
)
dp = Dispatcher()


@dp.message(CommandStart())
async def on_start(message: Message) -> None:
    cfg = store.get()
    if cfg.button_url:
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=cfg.button_text, url=cfg.button_url)]
            ]
        )
        await message.answer(cfg.message_text, reply_markup=keyboard)
    else:
        await message.answer(cfg.message_text)


@dp.message(F.text == "/ping")
async def on_ping(message: Message) -> None:
    await message.answer("ok")


async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )

    cfg = store.get()
    bots = [Bot(token=token) for token in cfg.tokens]

    logging.info("Запускаю %s ботов", len(bots))
    await dp.start_polling(*bots)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Остановка")
