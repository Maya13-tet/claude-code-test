# text-to-video

Проект для генерации коротких видео (по умолчанию ~15 секунд) из текстового описания через [KIE API](https://kie.ai) — модель `bytedance/seedance-2-fast`.

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
VIDEO_API_BASE_URL=https://api.kie.ai
VIDEO_API_KEY=your_kie_api_key_here
```

Ключ создаётся на https://kie.ai/api-key.

## Использование

```bash
python src/generate.py "Кот играет с клубком ниток на закате" --duration 15 --output out/video.mp4
```

## Как это работает

1. `submit_generation` — создаёт задачу через `POST /api/v1/jobs/createTask`
2. `poll_status` — опрашивает `GET /api/v1/jobs/recordInfo` (унифицированный эндпоинт для всех моделей Market) с экспоненциальной задержкой (3 → 30 сек), пока `state` не станет `success` или `fail`; таймаут — 15 минут
3. `download_result` — скачивает видео по ссылке из `resultUrls`

Учтите: ссылки на результат действительны ~24 часа, поэтому скачивание происходит сразу после успешного статуса. Допустимая длительность видео по API — 4–15 секунд (или -1).
