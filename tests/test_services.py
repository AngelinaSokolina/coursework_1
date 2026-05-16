import json
import pytest
from src.services import (
    format_date,
    easy_search,
    search_by_phone,
    search_by_person_transfer
)


@pytest.fixture
def test_data():
    """Создаёт тестовые данные для проверки функций"""
    return [
        {
            "Дата операции": "2024-01-15 10:30:00",
            "Категория": "Переводы",
            "Описание": "Перевод Ивану С. +7 995 555-55-55",
            "Сумма операции": 1000.50,
            "Валюта операции": "RUB"
        },
        {
            "Дата операции": "2024-02-20 14:00:00",
            "Категория": "Переводы",
            "Описание": "Перевод Петру А. на карту",
            "Сумма операции": 500.00,
            "Валюта операции": "USD"
        },
        {
            "Дата операции": "2024-03-10 09:15:00",
            "Категория": "Покупки",
            "Описание": "Оплата в магазине",
            "Сумма операции": 250.00,
            "Валюта операции": "RUB"
        },
        {
            "Дата операции": "2024-04-05 18:45:00",
            "Категория": "Переводы",
            "Описание": "Дмитрий Р. на карту",
            "Сумма операции": 3000.00,
            "Валюта операции": "EUR"
        },
        {"Дата операции": "2024-05-01",
         "Категория": "Покупки",
         "Описание": "Перевод Ивану С.",
         "Сумма операции": 100,
         "Валюта операции": "RUB"}
    ]


# ==================== format_date ====================

def test_format_date_with_valid_date():
    """Проверяет преобразование валидной даты"""
    result = format_date("2024-01-15")
    assert result == "15.01.2024"


def test_format_date_with_datetime():
    """Проверяет преобразование даты с временем"""
    result = format_date("2024-01-15 10:30:00")
    assert result == "15.01.2024"


def test_format_date_with_empty_string():
    """Проверяет обработку пустой строки"""
    result = format_date("")
    assert result == "Дата не указана"


# ==================== easy_search ====================

def test_easy_search_found(test_data):
    """Проверяет поиск существующего слова"""
    result_json = easy_search(test_data, "ПеРЕвод")
    result = json.loads(result_json)
    assert len(result) == 3


def test_easy_search_not_found(test_data):
    """Проверяет поиск несуществующего слова"""
    result_json = easy_search(test_data, "вчасмпирто")
    result = json.loads(result_json)
    assert len(result) == 0

# ==================== search_by_phone ====================

def test_search_by_phone_found(test_data):
    """Проверяет поиск существующего номера телефона"""
    result = search_by_phone(test_data, "+7 921 11-22-33")
    result_list = json.loads(result)
    assert len(result_list) == 1


def test_search_by_phone_not_found(test_data):
    """Проверяет поиск несуществующего номера"""
    result = search_by_phone(test_data, "+745744-22-33")
    assert "Некорректный номер: +457-22-33. Должно быть 11 цифр" in result


def test_search_by_phone_invalid_length(test_data):
    """Проверяет ввод номера неправильной длины"""
    result = search_by_phone(test_data, "123")
    assert "Некорректный номер" in result


# ==================== search_by_person_transfer ====================

def test_search_by_person_transfer_found(test_data):
    """Проверяет поиск существующего человека (русское имя)"""
    result = search_by_person_transfer(test_data, "Иван С.")
    assert result.startswith("[")
    result_list = json.loads(result)
    assert len(result_list) == 1
    assert "Иван С." in result_list[0]["Описание"]



def test_search_by_person_transfer_case_insensitive(test_data):
    """Проверяет регистронезависимый поиск"""
    result = search_by_person_transfer(test_data, "иван с.")
    assert result.startswith("[")
    result_list = json.loads(result)
    assert len(result_list) == 1


def test_search_by_person_transfer_not_found(test_data):
    """Проверяет поиск несуществующего человека"""
    result = search_by_person_transfer(test_data, "Вфвапр И.")
    assert "Переводов физическому лицу" in result



def test_search_by_person_transfer_invalid_format(test_data):
    """Проверяет ввод в неправильном формате"""
    result = search_by_person_transfer(test_data, "Иван")
    assert "Некорректный ввод" in result


def test_search_by_person_transfer_only_initial(test_data):
    """Проверяет ввод только инициала"""
    result = search_by_person_transfer(test_data, "С.")
    assert "Некорректный ввод" in result

