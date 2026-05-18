from unittest.mock import patch

from src.main import (
    get_greeting,
    display_card_info,
    display_top_transactions,
)


# ==================== get_greeting ====================

@patch('src.main.datetime')
def test_get_greeting_morning(mock_datetime):
    """Проверяет приветствие для утреннего времени (6-11)"""
    mock_datetime.now.return_value.hour = 8
    assert get_greeting() == "Доброе утро"


@patch('src.main.datetime')
def test_get_greeting_afternoon(mock_datetime):
    """Проверяет приветствие для дневного времени (12-17)"""
    mock_datetime.now.return_value.hour = 15
    assert get_greeting() == "Добрый день"


@patch('src.main.datetime')
def test_get_greeting_evening(mock_datetime):
    """Проверяет приветствие для вечернего времени (18-22)"""
    mock_datetime.now.return_value.hour = 20
    assert get_greeting() == "Добрый вечер"


@patch('src.main.datetime')
def test_get_greeting_night(mock_datetime):
    """Проверяет приветствие для ночного времени (23-5)"""
    mock_datetime.now.return_value.hour = 2
    assert get_greeting() == "Доброй ночи"


# ==================== display_card_info ====================

def test_display_card_info_with_valid_data(capsys):
    """Проверяет вывод информации о картах с корректными данными"""
    test_data = [
        {"Номер карты": "*6568", "Сумма операции": 1000.50, "Валюта операции": "RUB"},
        {"Номер карты": "*6568", "Сумма операции": 500.00, "Валюта операции": "RUB"},
        {"Номер карты": "*1234", "Сумма операции": 300.00, "Валюта операции": "USD"},
    ]

    display_card_info(test_data)
    captured = capsys.readouterr()

    assert "*6568: 1500.50 RUB" in captured.out
    assert "*1234: 300.00 USD" in captured.out


def test_display_card_info_with_empty_data(capsys):
    """Проверяет вывод при отсутствии данных о картах"""
    test_data = [
        {"Номер карты": None, "Сумма операции": 1000},
        {"Номер карты": "", "Сумма операции": 500},
        {"Сумма операции": 300},  # без поля "Номер карты"
    ]

    display_card_info(test_data)
    captured = capsys.readouterr()

    assert "Информация о картах не найдена" in captured.out


# ==================== display_top_transactions ====================

def test_display_top_transactions_with_valid_data(capsys):
    """Проверяет вывод топ-5 транзакций"""
    test_data = [
        {"Сумма операции": 100, "Категория": "Кафе", "Описание": "Обед", "Дата операции": "2024-01-01"},
        {"Сумма операции": 500, "Категория": "Ресторан", "Описание": "Ужин", "Дата операции": "2024-01-02"},
        {"Сумма операции": 300, "Категория": "Супермаркет", "Описание": "Продукты", "Дата операции": "2024-01-03"},
        {"Сумма операции": 200, "Категория": "Аптека", "Описание": "Лекарства", "Дата операции": "2024-01-04"},
        {"Сумма операции": 50, "Категория": "Транспорт", "Описание": "Такси", "Дата операции": "2024-01-05"},
    ]

    display_top_transactions(test_data, limit=3)
    captured = capsys.readouterr()

    # Проверяем сортировку по убыванию (500, 300, 200)
    assert "Топ-3 транзакций" in captured.out
    assert "500.0 руб." in captured.out
    assert "300.0 руб." in captured.out
    assert "200.0 руб." in captured.out


def test_display_top_transactions_with_less_than_limit(capsys):
    """Проверяет вывод при количестве транзакций меньше лимита"""
    test_data = [
        {"Сумма операции": 100, "Категория": "Кафе", "Описание": "Обед", "Дата операции": "2024-01-01"},
        {"Сумма операции": 50, "Категория": "Транспорт", "Описание": "Такси", "Дата операции": "2024-01-02"},
    ]

    display_top_transactions(test_data, limit=5)
    captured = capsys.readouterr()

    # Должны вывестись только 2 транзакции (столько, сколько есть)
    assert "Топ-5 транзакций" in captured.out
    assert "100.0 руб." in captured.out
    assert "50.0 руб." in captured.out


def test_display_top_transactions_with_string_amount(capsys):
    """Проверяет обработку суммы в виде строки"""
    test_data = [
        {"Сумма операции": "100.50", "Категория": "Кафе", "Описание": "Обед", "Дата операции": "2024-01-01"},
    ]

    display_top_transactions(test_data, limit=1)
    captured = capsys.readouterr()

    assert "100.5 руб." in captured.out
