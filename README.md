# Multi Telegram Start Bot

Софт для запуска сразу нескольких Telegram-ботов (например, 10+) с единым ответом на `/start`.

## Формат, как вы просили

### 1) Отдельный блокнот с токенами: `tokens.txt`

Каждый токен на новой строке:

```text
123456:AAA...
987654:BBB...
555555:CCC...
```

Можно держать хоть 10+ токенов.

### 2) Отдельный блокнот для текста: `message.txt`

Любой текст, который бот отправляет на `/start`.

### 3) (Опционально) Блокнот для кнопки

- `button_text.txt` — текст кнопки (по умолчанию `Перейти`)
- `button_url.txt` — ссылка кнопки (если пусто, кнопки не будет)

## Установка

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Быстрый старт

```bash
cp tokens.example.txt tokens.txt
cp message.example.txt message.txt
cp button_text.example.txt button_text.txt
cp button_url.example.txt button_url.txt
```

Заполните файлы и запустите:

```bash
python bot_manager.py
```

## Как менять сообщение быстро

Просто откройте `message.txt`, поменяйте текст и сохраните.
Новые значения подхватываются автоматически.
