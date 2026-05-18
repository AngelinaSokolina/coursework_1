import json

import pytest

from src.services import (easy_search, format_date,
                          get_top_cashback_categories,
                          search_by_person_transfer, search_by_phone)


@pytest.fixture
def test_data():
    """Создаёт тестовые данные для проверки функций"""
    return [
        {
            "Дата операции": "2024-01-15 10:30:00",
            "Категория": "Переводы",
            "Описание": "Перевод Иван С. +7 995 555-55-55",
            "Сумма операции": 1000.50,
            "Валюта операции": "RUB",
        },
        {
            "Дата операции": "2024-02-20 14:00:00",
            "Категория": "Переводы",
            "Описание": "Перевод Петр А. на карту",
            "Сумма операции": 500.00,
            "Валюта операции": "USD",
        },
        {
            "Дата операции": "2024-03-10 09:15:00",
            "Категория": "Покупки",
            "Описание": "Оплата в магазине",
            "Сумма операции": 250.00,
            "Валюта операции": "RUB",
        },
        {
            "Дата операции": "2024-04-05 18:45:00",
            "Категория": "Переводы",
            "Описание": "Перевод Дмитрий Р. на карту",
            "Сумма операции": 3000.00,
            "Валюта операции": "EUR",
        },
        {
            "Дата операции": "2024-05-01",
            "Категория": "Покупки",
            "Описание": "Перевод Ивану С.",
            "Сумма операции": 100,
            "Валюта операции": "RUB",
        },
    ]


# ==================== format_date ====================


def test_format_date_with_valid_date():
    result = format_date("2024-01-15")
    assert result == "15.01.2024"


def test_format_date_with_datetime():
    result = format_date("2024-01-15 10:30:00")
    assert result == "15.01.2024"


def test_format_date_with_empty_string():
    result = format_date("")
    assert result == "Дата не указана"


# ==================== easy_search ====================


def test_easy_search_found(test_data):
    result_json = easy_search(test_data, "Перевод")
    result = json.loads(result_json)
    assert len(result) == 4


def test_easy_search_not_found(test_data):
    result_json = easy_search(test_data, "вчасмпирто")
    result = json.loads(result_json)
    assert len(result) == 0


# ==================== search_by_phone ====================


def test_search_by_phone_found(test_data):
    result = search_by_phone(test_data, "+7 995 555-55-55")
    result_list = json.loads(result)
    assert len(result_list) == 1


def test_search_by_phone_not_found(test_data):
    result = search_by_phone(test_data, "+7 999 111-22-33")
    assert "Операций с номером" in result


def test_search_by_phone_invalid_length(test_data):
    result = search_by_phone(test_data, "123")
    assert "Некорректный номер" in result


# ==================== search_by_person_transfer ====================


def test_search_by_person_transfer_found(test_data):
    result = search_by_person_transfer(test_data, "Иван С.")
    assert result.startswith("[")
    result_list = json.loads(result)
    assert len(result_list) == 1
    assert "Иван С." in result_list[0]["Описание"]


def test_search_by_person_transfer_case_insensitive(test_data):
    result = search_by_person_transfer(test_data, "иван с.")
    assert result.startswith("[")
    result_list = json.loads(result)
    assert len(result_list) == 1


def test_search_by_person_transfer_not_found(test_data):
    result = search_by_person_transfer(test_data, "Вфвапр И.")
    assert "Переводов физическому лицу" in result


def test_search_by_person_transfer_invalid_format(test_data):
    result = search_by_person_transfer(test_data, "Иван")
    assert "Некорректный ввод" in result


def test_search_by_person_transfer_only_initial(test_data):
    result = search_by_person_transfer(test_data, "С.")
    assert "Некорректный ввод" in result


# ==================== get_top_cashback_categories ====================


def test_get_top_cashback_categories_normal():
    """Проверяет нормальную работу с разными категориями и бонусами"""
    test_data = [
        {"Категория": "Кафе", "Бонусы (включая кэшбэк)": 100.50},
        {"Категория": "Кафе", "Бонусы (включая кэшбэк)": 50.25},
        {"Категория": "Продукты", "Бонусы (включая кэшбэк)": 200.00},
        {"Категория": "Продукты", "Бонусы (включая кэшбэк)": 30.00},
        {"Категория": "Аптеки", "Бонусы (включая кэшбэк)": 80.00},
        {"Категория": "Такси", "Бонусы (включая кэшбэк)": 10.00},
    ]

    result = get_top_cashback_categories(test_data, top_n=3)

    assert len(result) == 3
    assert result[0]["Категория"] == "Продукты"
    assert result[0]["Бонусы"] == 230.00
    assert result[1]["Категория"] == "Кафе"
    assert result[1]["Бонусы"] == 150.75
    assert result[2]["Категория"] == "Аптеки"
    assert result[2]["Бонусы"] == 80.00


def test_get_top_cashback_categories_no_bonuses():
    """Проверяет, когда все бонусы нулевые или отсутствуют"""
    test_data = [
        {"Категория": "Кафе", "Бонусы (включая кэшбэк)": 0},
        {"Категория": "Продукты", "Бонусы (включая кэшбэк)": None},
        {"Категория": "Аптеки", "Бонусы (включая кэшбэк)": "нет"},
        {"Категория": "Такси", "Бонусы (включая кэшбэк)": ""},
    ]

    result = get_top_cashback_categories(test_data, top_n=5)
    assert result == []


def test_get_top_cashback_categories_string_bonus():
    """Проверяет, что бонусы в виде строк преобразуются в числа"""
    test_data = [
        {"Категория": "Кафе", "Бонусы (включая кэшбэк)": "100.50"},
        {"Категория": "Кафе", "Бонусы (включая кэшбэк)": "50.25"},
        {"Категория": "Продукты", "Бонусы (включая кэшбэк)": "200"},
    ]

    result = get_top_cashback_categories(test_data, top_n=2)

    assert len(result) == 2
    assert result[0]["Категория"] == "Продукты"
    assert result[0]["Бонусы"] == 200.00
    assert result[1]["Категория"] == "Кафе"
    assert result[1]["Бонусы"] == 150.75


def test_get_top_cashback_categories_with_negative_bonus():
    """Проверяет, что отрицательные бонусы тоже учитываются"""
    test_data = [
        {"Категория": "Кафе", "Бонусы (включая кэшбэк)": 100},
        {"Категория": "Кафе", "Бонусы (включая кэшбэк)": -50},
        {"Категория": "Продукты", "Бонусы (включая кэшбэк)": 80},
    ]

    result = get_top_cashback_categories(test_data, top_n=2)

    assert len(result) == 2
    assert result[0]["Категория"] == "Продукты"
    assert result[0]["Бонусы"] == 80.00
    assert result[1]["Категория"] == "Кафе"
    assert result[1]["Бонусы"] == 50.00


def test_get_top_cashback_categories_with_rounding():
    """Проверяет округление бонусов до 2 знаков"""
    test_data = [
        {"Категория": "Кафе", "Бонусы (включая кэшбэк)": 100.666},
        {"Категория": "Кафе", "Бонусы (включая кэшбэк)": 50.333},
    ]

    result = get_top_cashback_categories(test_data, top_n=1)

    assert result[0]["Бонусы"] == 151.00


def test_get_top_cashback_categories_mixed_data_types():
    """Проверяет смешанные типы данных в бонусах"""
    test_data = [
        {"Категория": "Кафе", "Бонусы (включая кэшбэк)": 100},
        {"Категория": "Кафе", "Бонусы (включая кэшбэк)": "50.5"},
        {"Категория": "Кафе", "Бонусы (включая кэшбэк)": None},
        {"Категория": "Кафе", "Бонусы (включая кэшбэк)": "не число"},
        {"Категория": "Кафе", "Бонусы (включая кэшбэк)": 0},
    ]

    result = get_top_cashback_categories(test_data, top_n=1)

    assert len(result) == 1
    assert result[0]["Категория"] == "Кафе"
    assert result[0]["Бонусы"] == 150.50
