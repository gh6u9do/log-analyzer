# Мини-гайд по pandas на 40 минут

Цель: освоить ровно те операции, которые использует `analyze_logs.py`.
Всё выполняйте в [Google Colab](https://colab.research.google.com) (новый блокнот) — ничего устанавливать не нужно.

## Шаг 1 (5 мин). Загрузка данных

В Colab слева откройте панель «Файлы» и загрузите `sample_logs/app.jsonl`,
затем в ячейке:

```python
import pandas as pd

df = pd.read_json('app.jsonl', lines=True)   # JSONL: каждая строка = объект
df.head()          # первые 5 строк
df.shape           # (600, 6) - 600 строк, 6 колонок
df.columns         # названия колонок
```

## Шаг 2 (10 мин). Подсчёт и фильтрация

```python
df['level'].value_counts()              # сколько записей каждого уровня
df['level'].value_counts(normalize=True)  # то же в долях

# фильтрация: только ошибки и fatal
errors = df[df['level'].isin(['error', 'fatal'])]
errors.shape

# два условия сразу
df[(df['level'] == 'error') & (df['status'] == 500)].shape
```

## Шаг 3 (10 мин). Группировка и сортировка

```python
# топ повторяющихся сообщений об ошибках
errors['message'].value_counts().head(5)

# среднее время ответа по endpoint'ам
df.groupby('endpoint')['duration_ms'].mean().sort_values(ascending=False)

# сколько ошибок на каждый endpoint
errors.groupby('endpoint').size().sort_values(ascending=False)
```

## Шаг 4 (10 мин). Время

```python
df['timestamp'] = pd.to_datetime(df['timestamp'])
df = df.set_index('timestamp')

# сколько записей в каждую минуту
per_minute = df.resample('1min').size()
per_minute.head()
per_minute.min(), per_minute.mean(), per_minute.max()

# только ошибки по времени
errors = df[df['level'].isin(['error', 'fatal'])]
errors.resample('5min').size()
```

## Шаг 5 (5 мин). Проверка себя

Откройте `analyze_logs.py` и найдите каждую из этих операций в коде.
Если вы понимаете, откуда берётся каждая цифра в отчёте — базы достаточно.

## Что дальше (по желанию)

Официальный туториал: https://pandas.pydata.org/docs/user_guide/10min.html —
разделы «Object Creation», «Viewing Data», «Selection», «Grouping»,
«Reshaping/Time series» закрывают 90% повседневных задач.
