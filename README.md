# Multi Telegram Start Bot

Готовый софт для запуска сразу нескольких Telegram-ботов (10+) с ответом на `/start`.

## Самое главное (чтобы не путаться)

Теперь используются **понятные файлы с номерами**:

- `01_tokens.txt` — токены ботов (1 токен = 1 строка)
- `02_start_message.txt` — текст, который приходит на `/start`
- `03_button_text.txt` — текст кнопки
- `04_button_url.txt` — ссылка кнопки

> Для совместимости старые имена (`tokens.txt`, `message.txt` и т.д.) тоже поддерживаются.

## Что происходит при первом запуске

- Если нет `01_tokens.txt`, программа создаст его с подсказками и попросит вставить токены.
- Если нет файлов сообщения/кнопки, они создаются автоматически с дефолтными значениями.
- Если `02_start_message.txt` пустой, берется дефолтный текст (ошибки не будет).

## Установка

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```


## Быстрый старт с примерами

```bash
cp 01_tokens.example.txt 01_tokens.txt
cp 02_start_message.example.txt 02_start_message.txt
cp 03_button_text.example.txt 03_button_text.txt
cp 04_button_url.example.txt 04_button_url.txt
```

## Запуск

```bash
python bot_manager.py
```

## Пример `01_tokens.txt`

```text
123456:AAA_BOT_TOKEN
987654:BBB_BOT_TOKEN
555555:CCC_BOT_TOKEN
```

## Как быстро сменить сообщение

Откройте `02_start_message.txt`, поменяйте текст и сохраните.
Изменение подхватится автоматически.
