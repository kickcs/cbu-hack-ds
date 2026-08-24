# RegTech — платформа статистического аудита банковской отчётности

Hackathon: CBU Coding Hackathon 2026 · FinTech. Статистический аудит реестра
банковских кредитов: закон Бенфорда + 5 детекторов нарушений по агрегированной
отчётности, ранжирование банков по подозрительности, дашборд аудитора.

## Стек

- **Бэкенд:** Python, FastAPI, pandas, scipy, SQLite (битемпоральная модель).
- **Фронтенд:** React + Vite + TypeScript + shadcn/ui (пресет `b3ad8zWp8z`).

## Быстрый старт

### Локально

```bash
# 1) Бэкенд (API на :8000)
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# 2) Фронтенд (на :5173)
cd frontend
npm install
npm run dev
```

Откройте http://localhost:5173 — кнопка «Перезапустить аудит» запускает полный
прогон, результат сохраняется в оба файла ТЗ: `результат/подозрительные_банки.csv`
и `natija/shubhali_banklar.csv`.

### Docker

```bash
docker compose up --build
# фронт:  http://localhost:5173
# API:    http://localhost:8000/docs
```

### Makefile

```bash
make run        # docker compose up --build
make audit      # бэкенд: python cli.py -> результат/подозрительные_банки.csv
make test       # pytest
make dev-backend
make dev-frontend
```

## Запуск аудита из CLI

```bash
cd backend && python cli.py --data .. --out ../результат/подозрительные_банки.csv
```

## Структура

```
backend/
  app/
    benford.py      # first_digit, benford_distribution, MAD, χ², пороги Нигрини
    ingest.py       # CSV/XLSX/XML -> каноническая модель + синонимы
    detectors.py    # threshold / rounding / arithmetic / discontinuity / window_dressing
    audit.py        # is_sample_sufficient(n), score_bank, rank_banks
    bootstrap.py    # бутстрап-калибровка порога (95-й перцентиль)
    db.py           # SQLite, битемпоральность (period + received_at)
    main.py         # FastAPI: /api/meta, /api/audit/run, /api/audit/latest, /api/banks/{bank}/benford
  tests/            # pytest: benford + guard n<300 + детекторы + ingestion
  DECISIONS.md      # обоснование алгоритмов, порогов, Big-O, краевых случаев
  cli.py            # автономный прогон аудита в CSV
frontend/
  src/App.tsx       # дашборд аудитора
  src/lib/api.ts    # клиент API
  src/components/benford-chart.tsx
результат/подозрительные_банки.csv   # русская версия ТЗ (банк, значение_mad, причина)
natija/shubhali_banklar.csv          # официальная версия ТЗ (bank, mad_qiymati, sabab)
Makefile
docker-compose.yml
```

## API

| Метод | Путь | Описание |
|---|---|---|
| GET | `/api/health` | статус + `min_sample` |
| GET | `/api/meta` | список банков, размер реестра, недостаточные выборки |
| POST | `/api/audit/run` | полный прогон аудита (персист в SQLite + CSV) |
| GET | `/api/audit/latest` | ранжированные результаты всех тестов |
| GET | `/api/banks/{bank}/benford` | распределение первых цифр + метрики |

## Результат на образце данных

6 банков признаны подозрительными (precision=1.00, recall=1.00 против ключа
ответа), причины совпадают с эталонными типами нарушений.

```
Davr Bank       threshold | rounding
Asaka Bank      threshold
Hamkor Bank     discontinuity
Universal Bank  window_dressing
Aloqa Bank      benford
Kapital Bank    arithmetic
```

## Тесты

```bash
cd backend && python -m pytest tests/ -q
```

- Синтетика, честно следующая Бенфорду → MAD ≈ 0.
- Выборка `n < 300` → флаг `insufficient_sample`, а не числовой MAD.
- Детекторы: порог/округление/арифметика/разрыв/window dressing на синтетике.
- Ingestion: 100% названий показателей сопоставлены во всех трёх форматах.
