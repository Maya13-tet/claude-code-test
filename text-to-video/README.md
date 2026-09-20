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

## Статус интеграции с KIE

- `submit_generation` — реализована по документации `POST /api/v1/jobs/createTask` (модель `bytedance/seedance-2-fast`)
- `poll_status` — черновая реализация под `GET /api/v1/jobs/recordInfo`; точная схема ответа ("Get Task Details") не была подтверждена документацией на момент написания — сверьте названия полей статуса/результата перед использованием
- `duration` — по API допустимо 4–15 секунд (или -1)
