import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd

from src.services import (easy_search, excel_data, format_date,
                          get_top_cashback_categories,
                          search_by_person_transfer, search_by_phone)


def get_greeting() -> str:
    """Возвращает приветствие в зависимости от времени суток"""
    hour = datetime.now().hour
    if 6 <= hour < 12:
        return "Доброе утро"
    elif 12 <= hour < 18:
        return "Добрый день"
    elif 18 <= hour < 23:
        return "Добрый вечер"
    else:
        return "Доброй ночи"


def display_card_info(data: List[Dict[str, Any]]) -> None:
    """Выводит информацию о картах из транзакций: группирует по номеру карты, суммирует операции"""
    cards_info = {}

    for row in data:
        card_number = row.get("Номер карты", "")
        if pd.isna(card_number) or not card_number:
            continue

        amount_raw = row.get("Сумма операции", 0)
        try:
            amount = float(amount_raw) if amount_raw else 0
        except (ValueError, TypeError):
            amount = 0

        if card_number not in cards_info:
            cards_info[card_number] = {
                "total": 0,
                "currency": row.get("Валюта операции", "RUB"),
            }
        cards_info[card_number]["total"] += amount

    if not cards_info:
        print("Информация о картах не найдена")
        return

    print("\nИнформация о картах")
    for card, info in cards_info.items():
        print(f"{card}: {info['total']:.2f} {info['currency']}")


def display_top_transactions(data: List[Dict[str, Any]], limit: int = 5) -> None:
    """Выводит топ-5 транзакций, отсортированных по убыванию суммы"""
    sorted_data = sorted(
        data, key=lambda x: float(x.get("Сумма операции", 0)), reverse=True
    )

    print(f"\nТоп-{limit} транзакций \n")

    for i, row in enumerate(sorted_data[:limit], 1):
        amount = float(row.get("Сумма операции", 0))
        category = row.get("Категория", "Без категории")
        description = row.get("Описание", "Без описания")
        date_raw = row.get("Дата операции", "")

        print(
            f"{i}. {format_date(date_raw)} | {amount:} руб. | {category} | {description[:50]}"
        )


def main() -> None:
    """Главная функция"""

    print(
        f"{get_greeting()}! \nДобро пожаловать в программу анализа банковских транзакций.\n"
    )

    data = excel_data(Path(__file__).parent.parent / "data" / "operations.xlsx")

    if not data:
        print("Не удалось загрузить данные")
        return

    display_card_info(data)
    display_top_transactions(data, limit=5)
    get_top_cashback_categories(data, top_n=3)

    print("\nПоиск по телефону")
    phone_result = search_by_phone(data, "+7 995 555-55-55")
    if phone_result.startswith("["):
        result_list = json.loads(phone_result)
        print(f"Найдено транзакций: {len(result_list)}")
    else:
        print(phone_result)

    print("\nПоиск по подстройке 'перевод'")
    search_result = easy_search(data, "перевод")
    result_list = json.loads(search_result)
    print(f"Найдено транзакций: {len(result_list)}")

    print("\nПоиск переводов физическим лицам")
    person_result = search_by_person_transfer(data, "Иван С.")
    if person_result.startswith("["):
        result_list = json.loads(person_result)
        print(f"Найдено переводов: {len(result_list)}")
    else:
        print(person_result)


if __name__ == "__main__":
    main()
