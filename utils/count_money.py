from typing import Optional

from db import db
from models import Money


def count_money(date, cinema_id: int, income: int, cash: int = 0, card: int = 0, expense: int = 0) -> Optional[Money]:
    """
    Функция проверяет существует ли запись для отведенных дней. \n
    Если есть то проводит калькуяции, если нет, то создает и проводит. \n
    Деньги поступают на счет только после того как статус транзакции становится finished.
    :param date:str -> обязательный параметр
    :param cinema_id:int -> обязательный параметр
    :param income:int -> Сколько пришло за аренду
    :param cash int -> Сколько из этого налик
    :param card -> Сколько из этого по карте
    :param expense -> Сколько из этого надо вычесть
    :return: Money -> объект Money
    """

    money_record = Money.query.filter(Money.date == date).filter(Money.cinema_id == cinema_id).first()

    if money_record is None:
        money_record = Money(date=date,
                             income=int(income),
                             expense=int(expense),
                             all_by_card=int(card),
                             all_by_cash=int(cash),
                             proceeds=int(income) - expense,
                             cinema_id=cinema_id)
        money_record.cashier_end = int(money_record.cashier_start) - expense + int(cash)
        try:
            db.session.add(money_record)
            return money_record
        except:
            return None

    money_record.income += int(income)
    money_record.expense += int(expense)
    money_record.proceeds = money_record.income - money_record.expense
    money_record.all_by_card += int(card)
    money_record.all_by_cash += int(cash)
    money_record.cashier_end = int(money_record.cashier_start) - \
                               int(money_record.expense) + int(money_record.all_by_cash)

    return money_record
