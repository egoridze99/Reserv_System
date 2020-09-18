import builtins
import datetime as dt

from models import *


def get_sum_of_checkouts(checkouts: list) -> int:
    sum_of_checkouts = 0

    for checkout in checkouts:
        sum_of_checkouts += int(checkout.summ)

    return sum_of_checkouts


def count_money(date, income: int, cash: int, card: int, expense: int) -> Money or None:
    """
    Функция проверяет существует ли запись для отведенных дней. \n
    Если есть то проводит калькуяции, если нет, то создает и проводит. \n
    Деньги поступают на счет только после того как статус транзакции становится finished.
    :param date:str -> обязательный параметр
    :param income:int -> Сколько пришло за аренду
    :param cash int -> Сколько из этого налик
    :param card -> Сколько из этого по карте
    :param expense -> Сколько из этого надо вычесть
    :return: Money -> объект Money
    """

    money_record = Money.query.filter(Money.date == date).first()

    if money_record is None:
        money_record = Money(date=date,
                             income=int(income),
                             expense=int(expense),
                             all_by_card=int(card),
                             all_by_cash=int(cash),
                             proceeds=int(income) - expense)
        money_record.cashier_end = int(money_record.cashier_start) - expense + int(cash)
        try:
            db.session.add(money_record)
            return money_record
        except builtins.TypeError:
            return None

    money_record.income += int(income)
    money_record.expense += int(expense)
    money_record.proceeds = money_record.income - money_record.expense
    money_record.all_by_card += int(card)
    money_record.all_by_cash += int(cash)
    money_record.cashier_end = int(money_record.cashier_start) - \
                               int(money_record.expense) + int(money_record.all_by_cash)

    try:
        db.session.add(money_record)
        return money_record
    except builtins.TypeError:
        return None


def get_money_record(date) -> dict:
    """Возвращает запись из таблицы с указанной датой"""

    money_record = Money.query.filter(Money.date == date).first()

    if money_record is not None:
        return {
            "id": money_record.id,
            "date": str(money_record.date),
            "income": money_record.income,
            "expense": money_record.expense,
            "proceeds": money_record.proceeds,
            "cashier_start": money_record.cashier_start,
            "cashier_end": money_record.cashier_end,
            "all_by_card": money_record.all_by_card,
            "all_by_cash": money_record.all_by_cash,
        }

    return {}


def is_date_in_last(date):
    now = datetime.now().date()
    return now > date


def check_the_taking(date, room, time, duration):
    """Проверяет занят ли зал"""

    reservs = Reservation\
        .query\
        .filter(Reservation.date == date)\
        .filter(Reservation.room == room)\
        .all()

    for reserv in reservs:
        if reserv.status == ReservStatusEnum.canceled:
            continue

        reserv_start_time = reserv.time
        delta = timedelta(hours=reserv.duration)
        reserv_end_time = (dt.datetime.combine(dt.date(1, 1, 1), reserv_start_time) + delta).time()

        new_delta = timedelta(hours=reserv.duration)
        new_reserv_end_time = (dt.datetime.combine(dt.date(1, 1, 1), time) + new_delta).time()

        if time == reserv_start_time:
            return True

        if time < reserv_start_time <= new_reserv_end_time:
            return True

        if reserv_start_time < time <= reserv_end_time:
            return True

    return False
