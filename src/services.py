import json
import re
from pathlib import Path
from typing import List, Dict, Any

import pandas as pd


def excel_data(file_path: str | Path) -> list[dict]:
    """Загружает данные из Excel и возвращает список словарей"""
    df = pd.read_excel(file_path, engine='openpyxl')
    return df.to_dict('records')


def format_date(date_str: str) -> str:
    """Преобразует дату в формат DD.MM.YYYY"""
    if not date_str:
        return "Дата не указана"

    # Берём только дату (до пробела)
    if ' ' in str(date_str):
        date_str = str(date_str).split(' ')[0]

    parts = re.findall(r'\d+', str(date_str))
    if len(parts) == 3:
        if len(parts[0]) == 4:
            return f"{parts[2]}.{parts[1]}.{parts[0]}"
        else:
            return f"{parts[0]}.{parts[1]}.{parts[2]}"
    return str(date_str)


def easy_search(data: List[Dict[str, Any]], search_str: str) -> str:
    """ Простой поиск по категории или описанию.
    Возвращает JSON-строку с отфильтрованными транзакциями """
    result = []
    search_lower = search_str.lower()

    for row in data:
        category_raw = row.get("Категория", "")
        category = "Данные отсутствуют" if pd.isna(category_raw) else str(category_raw)

        description_raw = row.get("Описание", "")
        description = "Данные отсутствуют" if pd.isna(description_raw) else str(description_raw)

        if search_lower in category.lower() or search_lower in description.lower():
            # Сумма и валюта из соответствующих колонок
            amount_raw = row.get("Сумма операции", 0)
            amount = float(amount_raw) if amount_raw else 0
            currency_raw = row.get("Валюта операции", "RUB")
            currency = str(currency_raw) if not pd.isna(currency_raw) else "RUB"

            result.append({
                "Дата": format_date(row.get("Дата операции", "")),
                "Сумма": amount,
                "Валюта": currency,
                "Описание": description,
                "Категория": category
            })

    return json.dumps(result, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    data = excel_data(Path(__file__).parent.parent / 'data' / 'operations.xlsx')
    search_query = input("Введите слово для поиска: ")
    result_json = easy_search(data, search_query)

    # Преобразуем JSON обратно в список, чтобы проверить длину
    result_list = json.loads(result_json)

    if result_list:
    # Если True
        print(result_json)
    # Если False
    else:
        print("Операции не обнаружено, попробуйте еще раз")