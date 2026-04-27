import asyncio
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

DEFAULT_START_MESSAGE = (
    "👋 Добро пожаловать! Мы запустили новую версию бота.\n\n"
    "👇 Перейдите по кнопке ниже."
)
DEFAULT_BUTTON_TEXT = "Перейти"

TOKENS_FILES = [Path("01_tokens.txt"), Path("tokens.txt")]
MESSAGE_FILES = [Path("02_start_message.txt"), Path("message.txt")]
BUTTON_TEXT_FILES = [Path("03_button_text.txt"), Path("button_text.txt")]
BUTTON_URL_FILES = [Path("04_button_url.txt"), Path("button_url.txt")]


@dataclass
class RuntimeConfig:
    tokens: List[str]
    message_text: str
    button_text: str
    button_url: str


class FileConfigStore:
    def __init__(
        self,
        tokens_files: List[Path],
        message_files: List[Path],
        button_text_files: List[Path],
        button_url_files: List[Path],
    ):
        self.tokens_files = tokens_files
        self.message_files = message_files
        self.button_text_files = button_text_files
        self.button_url_files = button_url_files
        self._mtimes = {}
        self._config: RuntimeConfig | None = None

    def _active_path(self, candidates: Iterable[Path]) -> Path:
        candidates = list(candidates)
        for path in candidates:
            if path.exists():
                return path
        return candidates[0]

    def _read_tokens(self) -> List[str]:
        tokens_path = self._active_path(self.tokens_files)
        if not tokens_path.exists():
            tokens_path.write_text(
                "# Вставьте сюда токены ботов: 1 токен = 1 строка\n"
                "# Пример:\n"
                "# 123456:ABCDEF_your_token\n",
                encoding="utf-8",
            )
            raise ValueError(
                f"Создан файл {tokens_path}. Вставьте в него токены и запустите снова."
            )

        tokens = [
            line.strip()
            for line in tokens_path.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.strip().startswith("#")
        ]

        if not tokens:
            raise ValueError(
                f"Файл {tokens_path} пустой. Добавьте минимум 1 токен (по одному на строку)."
            )

        return tokens

    def _read_text_or_default(self, files: List[Path], default: str) -> str:
        path = self._active_path(files)
        if not path.exists():
            path.write_text(default, encoding="utf-8")
            return default

        text = path.read_text(encoding="utf-8").strip()
        return text or default

    def _tracked_paths(self) -> List[Path]:
        return [
            self._active_path(self.tokens_files),
            self._active_path(self.message_files),
            self._active_path(self.button_text_files),
            self._active_path(self.button_url_files),
        ]

    def _is_changed(self) -> bool:
        for file in self._tracked_paths():
            current_mtime = file.stat().st_mtime if file.exists() else -1.0
            if self._mtimes.get(file) != current_mtime:
                return True

        return self._config is None

    def load_if_changed(self) -> None:
        if not self._is_changed():
            return

        tokens = self._read_tokens()
        message_text = self._read_text_or_default(
            self.message_files, DEFAULT_START_MESSAGE
        )
        button_text = self._read_text_or_default(
            self.button_text_files, DEFAULT_BUTTON_TEXT
        )
        button_url = self._read_text_or_default(self.button_url_files, "")

        self._config = RuntimeConfig(
            tokens=tokens,
            message_text=message_text,
            button_text=button_text,
            button_url=button_url,
        )

        for file in self._tracked_paths():
            self._mtimes[file] = file.stat().st_mtime if file.exists() else -1.0

        logging.info("Конфиг загружен: %s ботов", len(tokens))

    def get(self) -> RuntimeConfig:
        self.load_if_changed()
        if self._config is None:
            raise RuntimeError("Конфиг не загружен")
        return self._config


store = FileConfigStore(
    TOKENS_FILES,
    MESSAGE_FILES,
    BUTTON_TEXT_FILES,
    BUTTON_URL_FILES,
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
