import requests
import xml.etree.ElementTree as ET
from datetime import datetime


CBR_DAILY_URL = "http://www.cbr.ru/scripts/XML_daily.asp"


def get_currency_list() -> list[str]:
    """Возвращает список доступных валют (CharCode) с сайта ЦБ РФ."""
    response = requests.get(CBR_DAILY_URL, timeout=10)
    if response.status_code != 200:
        raise Exception("Не удалось получить список валют.")

    root = ET.fromstring(response.content)
    currencies = ["RUB"]

    for valute in root.findall("Valute"):
        char_code = valute.find("CharCode").text
        currencies.append(char_code)

    return currencies


def get_exchange_rate(date: str) -> dict[str, float]:
    """
    Возвращает словарь курсов валют к рублю на указанную дату.

    :param date: дата в формате DD/MM/YYYY
    :return: { 'USD': 92.5, 'EUR': 100.1, ... }
    """
    url = f"{CBR_DAILY_URL}?date_req={date}"
    response = requests.get(url, timeout=10)

    if response.status_code != 200:
        raise Exception("Не удалось получить курсы валют.")

    root = ET.fromstring(response.content)
    rates = {}

    for valute in root.findall("Valute"):
        char_code = valute.find("CharCode").text
        nominal = float(valute.find("Nominal").text)
        value = float(valute.find("Value").text.replace(",", "."))
        rates[char_code] = value / nominal

    return rates


def get_today_rate() -> dict[str, float]:
    """Возвращает курсы валют на сегодня."""
    today = datetime.now().strftime("%d/%m/%Y")
    return get_exchange_rate(today)
