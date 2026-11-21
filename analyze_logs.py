# -*- coding: utf-8 -*-
"""Анализатор логов веб-приложения.

Читает лог-файл в формате JSONL или TSKV и выводит сводную статистику:
количество записей по уровням, доля ошибок, топ сообщений об ошибках,
запросов в минуту и распределение HTTP-статусов.

Форматы соответствуют логгерам приложения Film React Nest
(JSON и TSKV с выбором через переменные окружения).

Запуск:
    python analyze_logs.py sample_logs/app.jsonl
    python analyze_logs.py sample_logs/app.tskv --format tskv
"""
import argparse
import json

import pandas as pd


def read_jsonl(path: str) -> pd.DataFrame:
    """Читает JSONL: каждая строка файла - один JSON-объект."""
    with open(path, encoding='utf-8') as f:
        return pd.DataFrame(json.loads(line) for line in f if line.strip())


def read_tskv(path: str) -> pd.DataFrame:
    """Читает TSKV: строка 'tskv\\tkey=value\\tkey=value...'."""
    rows = []
    with open(path, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line.startswith('tskv'):
                continue
            record = {}
            for part in line.split('\t')[1:]:
                if '=' in part:
                    key, value = part.split('=', 1)
                    record[key] = value
            rows.append(record)
    return pd.DataFrame(rows)


def load_logs(path: str, fmt: str) -> pd.DataFrame:
    if fmt == 'json':
        return read_jsonl(path)
    return read_tskv(path)


def print_report(df: pd.DataFrame) -> None:
    total = len(df)
    print(f'Всего записей в логе: {total}\n')

    # Записи по уровням логирования
    print('Записи по уровням:')
    print(df['level'].value_counts().to_string(), end='\n\n')

    # Доля ошибок
    errors = df[df['level'].isin(['error', 'fatal'])]
    print(f'Ошибок (error+fatal): {len(errors)} '
          f'({len(errors) / total:.1%} от всех записей)\n')

    # Топ повторяющихся сообщений об ошибках
    if len(errors):
        print('Топ-10 сообщений об ошибках:')
        top = (errors['message'].value_counts().head(10))
        for message, count in top.items():
            print(f'  {count:>4}  {message}')
        print()

    # Записей в минуту
    if 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        per_minute = df.set_index('timestamp').resample('1min').size()
        print(f'Записей в минуту: min={per_minute.min()}, '
              f'среднее={per_minute.mean():.1f}, max={per_minute.max()}\n')

    # HTTP-статусы, если они есть в логе
    if 'status' in df.columns:
        print('HTTP-статусы:')
        statuses = df['status'].astype('Int64')
        print(statuses.value_counts().sort_index().to_string())


def main() -> None:
    parser = argparse.ArgumentParser(description='Анализатор логов JSONL/TSKV')
    parser.add_argument('logfile', help='путь к файлу лога')
    parser.add_argument('--format', choices=['json', 'tskv'], default='json',
                        help='формат лога (по умолчанию json)')
    args = parser.parse_args()

    df = load_logs(args.logfile, args.format)
    print_report(df)


if __name__ == '__main__':
    main()
