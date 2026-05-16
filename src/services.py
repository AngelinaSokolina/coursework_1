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


def search_by_phone(data: List[Dict[str, Any]], phone_number: str) -> str:
    """Возвращает JSON с транзакциями, содержащими указанный номер телефона (точное совпадение)"""

    # Очищаем введённый номер от нецифровых символов
    phone_clean = re.sub(r'\D', '', phone_number)

    # Если после очистки нет 11 цифр — номер некорректный
    if len(phone_clean) != 11:
        return f"Некорректный номер: {phone_number}. Должно быть 11 цифр"

    # Первая цифра должна быть 7 или 8
    if phone_clean[0] not in ('7', '8'):
        return f"Некорректный номер: {phone_number}. Должен начинаться с +7 или 8"
    result = []

    for row in data:
        description = str(row.get('Описание', ''))

        # Находим все последовательности из 11 цифр подряд
        found_numbers = re.sub(r'\D', '', description)

        # Проверяем, есть ли среди них наш номер
        if phone_clean in found_numbers:
            result.append(row)

    if not result:
        return f"Операций с номером {phone_number} не найдено"

    return json.dumps(result, ensure_ascii=False, indent=4)


def search_by_person_transfer(data: List[Dict[str, Any]], person_name: str) -> str:
    """Возвращает JSON с транзакциями по переводам физических лиц"""

    # Очищаем введённую строку
    search_clean = person_name.strip().lower()

    # Проверка формата ввода: должно быть "имя буква."
    name_pattern = re.compile(r'^[а-я]+\s+[а-я]\.$', re.IGNORECASE)

    if not name_pattern.match(search_clean):
        return "Некорректный ввод. Используйте формат 'Имя Ф.',например, 'Иван С.'"

    # Паттерн для поиска в описании: слово на русском или английском + пробел + буква с точкой
    # [А-Яа-я] - любые буквы русского алфавита
    # + - одно или более вхождений
    # [А-Я] - одна заглавная буква
    # \. - точка
    person_pattern = re.compile(r'([А-Яа-я]+)\s+([А-Я])\.')

    result = []

    for row in data:
        category_raw = row.get('Категория', '')
        category = "Данные отсутствуют" if pd.isna(category_raw) else str(category_raw)

        description = str(row.get('Описание', ''))

        # Только переводы
        if category != 'Переводы':
            continue

        # Ищем в описании имя и инициал
        match = person_pattern.search(description)
        if not match:
            continue

        # Получаем найденное имя и инициал
        full_name = (f"{match.group(1)} {match.group(2)}.").lower()

        # Сравниваем с введённой строкой (очищенной)
        if  full_name == search_clean:
            result.append(row)

    if not result:
        return f"Переводов физическому лицу '{person_name}' не найдено"

    return json.dumps(result, ensure_ascii=False, indent=4)

if __name__ == '__main__':
    data = excel_data(Path(__file__).parent.parent / 'data' / 'operations.xlsx')

    # ===== Простой поиск ====
    search_query = input("Введите слово для поиска: ")
    result_json_easy_search = easy_search(data, search_query)

    # Преобразуем JSON обратно в список, чтобы проверить длину
    result_list = json.loads(result_json_easy_search)

    if result_list:
    # Если True
        print(result_json_easy_search)
    # Если False
    else:
        print("Операции не обнаружено, попробуйте еще раз")

    # ===== Для поиска по телефонным номерам ====
    phone_result = search_by_phone(data, "+7 995 555-55-55")
    print(phone_result)

    # ===== Для поиска переводов физическим лицам ====
    person_result = search_by_person_transfer(data, "Иван С.")
    print(person_result)

