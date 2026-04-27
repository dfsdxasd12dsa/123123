# Multi Telegram Start Bot

Максимально простой запуск нескольких Telegram-ботов.

## Нужно всего 4 блокнота

1. `tokens.txt` — все токены, по одному в строке
2. `message.txt` — текст сообщения на `/start`
3. `button_url.txt` — ссылка кнопки
4. `button_text.txt` — текст кнопки

Если `button_url.txt` пустой — кнопка не показывается.

## Установка

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
pip install -r requirements.txt
```

## Запуск

```bash
python bot_manager.py
```

При первом запуске файлы создаются автоматически.

## Пример `tokens.txt`

```text
123456:AAA_BOT_TOKEN
987654:BBB_BOT_TOKEN
```
