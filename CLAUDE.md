# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Что это

Хакатон CBU Coding Hackathon 2026 (FinTech): статистический аудит реестра банковских кредитов — закон Бенфорда + 5 детекторов нарушений по агрегированной отчётности, ранжирование банков по подозрительности, дашборд аудитора. Обоснование алгоритмов и порогов — в `DECISIONS.md` в корне (при изменении алгоритмов/порогов обновлять его обязательно — это часть сдачи). Ключ ответа для самопроверки: `_javob_kaliti/`.

Входные данные лежат в `data/` (`kredit_reyestri.csv`, `normativlar.csv`, `banklar.csv`, каталоги `csv/ xlsx/ xml/`) — бэкенд читает их через `DATA_DIR` (по умолчанию `data/` в корне репо). Каталог отдан под сырьё целиком: `iter_data_files` рекурсивно читает всё, что в нём лежит, поэтому ключ ответа и файлы результата остаются уровнем выше. Результаты пишутся в `output_dir` — по умолчанию родитель `data_dir`, то есть корень репо (`config.py`).

## Команды

```bash
make run          # docker compose up --build (фронт :5173, API :8000/docs)
make test         # cd backend && python3 -m pytest tests/ -q
make audit        # CLI-прогон: backend/cli.py -> результат/подозрительные_банки.csv
make dev-backend  # uvicorn app.main:app --reload --port 8000 (нужен .venv с requirements.txt)
make dev-frontend # cd frontend && npm run dev

# один тест
cd backend && python3 -m pytest tests/test_benford.py::test_small_sample_returns_insufficient_flag -q

# фронтенд
cd frontend && npm run lint / typecheck / build / format
```

## Архитектура

Пайплайн бэкенда (Python/FastAPI/pandas/scipy/SQLAlchemy+SQLite, конфиг и модели на pydantic):

1. `app/ingest/` — CSV/XLSX/XML → каноническая модель из 13 показателей: `readers.py` (по ридеру на формат), `indicators.py` (нормализация + словарь синонимов + fuzzy-fallback на `difflib`), `register.py` (форма реестра: где имя банка, где суммы). Должен работать на закрытом датасете второго дня с другими значениями/названиями. `classify.py` определяет `Role` файла (реестр / нормативы / отчётность / неопознан), `validation.py` возвращает `Issue(level, code, message, file)` по дефектам данных, `dataset.py` собирает `load_dataset(dir)`; `iter_data_files` пропускает каталоги с точки — на этом держится изоляция загруженных заявок.
2. `app/benford/` — `law.py` (первые цифры, MAD, χ², пороги Нигрини: подозрителен при MAD > 0.015) и `calibration.py` (бутстрап-калибровка порога, 95-й перцентиль MAD на синтетике — показывается в дашборде как подтверждение, но решение принимает порог Нигрини).
3. `app/detectors/` — по модулю на тип нарушения плюс `registry.py` (порядок детекторов = порядок причин в файле результата) и `functional.py` (`detect_*` для тестов). Решающие: threshold, rounding, arithmetic, discontinuity, window_dressing; совещательные (не влияют на вердикт): last_digit, balance. Пороги обоснованы в DECISIONS.md §4. `base.py`: `Detector.requires` объявляет нужные детектору таблицы, `runnable(DETECTORS, ctx)` отбирает выполнимые — непройденный тест попадает в `skipped`, а не в «пройдено».
4. `app/sampling.py` — `MIN_SAMPLE = 300` и `is_sample_sufficient(n)`. Guard `n < 300` — критическое требование ТЗ §5: без него решение не засчитывается; Бенфорд считается только по `kredit_reyestri.csv`, не по агрегату.
5. `app/audit/` — `benford_test.py` (тест по одному банку), `pipeline.py` (`audit_all`, `rank_banks`), `results.py` (формат файла результата), `evidence.py` (детализация улик для дашборда).
6. `app/storage/` — `tables.py` (модели SQLAlchemy) и `repository.py` (`AuditRepository`); битемпоральность: `period` и `received_at` раздельно, сырые файлы сохраняются байт-в-байт в `raw_files`.
7. `app/submissions/` — загруженные отчёты как отдельные заявки: `queue.py` (однопоточный фоновый воркер, `queued → processing → done|failed`), `runner.py` (аудит одной заявки поверх `.uploads/<id>/`), `repository.py` (`submissions` в той же SQLite), `service.py`. Заявка изолирована от общего датасета структурно, а не флагом — см. DECISIONS.md §8.
8. `app/service.py` — `AuditService`, один пайплайн для API и CLI; `app/api/` — фабрика приложения, `deps.py`, `schemas.py` и роуты в `api/routes/{health,meta,audit,banks,submissions}.py`; `app/main.py` — только точка входа `app.main:app`.

Результат пишется в оба варианта ТЗ (форматы и имена проверяются автопроверкой, не менять): `результат/подозрительные_банки.csv` (`банк, значение_mad, причина` — русская версия §8) и `natija/shubhali_banklar.csv` (`bank, mad_qiymati, sabab` — официальная версия §5); значения идентичны. На образце precision=recall=1.00 против ключа ответа — изменения алгоритмов не должны это ломать (`make audit` + сверка с `_javob_kaliti/`).

Тесты (`backend/tests/`) построены на синтетике (`synthetic.py`): честный Бенфорд → MAD ≈ 0; `n < 300` → флаг `insufficient_sample`, а не число; каждый детектор ловит свой тип нарушения; ingestion сопоставляет 100% названий во всех трёх форматах.

Фронтенд: React 19 + Vite + TypeScript + Tailwind v4 + shadcn/ui, разложен по Feature-Sliced Design (`app / pages / widgets / features / entities / shared`). HTTP-клиент — `shared/api/client.ts` (адрес API — `VITE_API_URL`, по умолчанию :8000), запросы к бэкенду — в `entities/{audit,bank,submission}/api/`. Четыре маршрута: матрица (`/`), досье банка (`/bank/<имя>`), приёмная (`/filings`) и отчёт по заявке (`/filings/<id>`); пути собираются в `shared/lib/routes.ts`, роутер свой — `shared/lib/router.tsx` на History API, SPA-фолбэк для прода уже есть в `frontend/nginx.conf`. Незавершённые заявки опрашиваются через `refetchInterval` в `entities/submission/api/`; опрос сам останавливается, когда очередь пуста.
