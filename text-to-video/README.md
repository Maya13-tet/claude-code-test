# text-to-video

Заготовка проекта для генерации коротких видео (по умолчанию ~15 секунд) из текстового описания через внешний API генерации видео (например, Runway, Replicate, Luma, Pika, Sora API и т.п.).

Сам вызов сгенерирован не будет — здесь только структура проекта и клиент, который нужно подключить к конкретному провайдеру.

## Структура

```
text-to-video/
├── README.md
├── requirements.txt
├── .env.example
└── src/
    └── generate.py   # CLI для генерации видео по тексту
```

## Установка

```bash
cd text-to-video
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Заполните `.env`:

```
VIDEO_API_BASE_URL=https://api.example.com
VIDEO_API_KEY=your_api_key_here
```

## Использование

```bash
python src/generate.py "Кот играет с клубком ниток на закате" --duration 15 --output out/video.mp4
```

## Подключение реального провайдера

В `src/generate.py` функции `submit_generation`, `poll_status` и `download_result` содержат заглушки — их нужно заменить на конкретные эндпоинты выбранного сервиса (см. документацию провайдера). Общая логика (CLI, ожидание, сохранение файла) уже готова.
