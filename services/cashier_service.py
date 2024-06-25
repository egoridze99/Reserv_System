from datetime import datetime

from sqlalchemy import func, text

from db import db
from models import Transaction, Cinema, City, TransactionStatusEnum, TransactionTypeEnum


class CashierService:
    @staticmethod
    def __get_base_query(date: datetime.date, cinema_id: int):
        return db.session.query(func.sum(Transaction.sum)) \
            .join(Cinema) \
            .join(City) \
            .filter(Transaction.cinema_id == cinema_id) \
            .filter(Transaction.transaction_status == TransactionStatusEnum.completed) \
            .filter(text("""date(get_shift_date("transaction".created_at, city.timezone, 0)) = :target_date""")) \
            .params(target_date=date)

    @staticmethod
    def __get_income(date: datetime.date, cinema_id: int):
        return CashierService.__get_base_query(date, cinema_id).filter(Transaction.sum >= 0).scalar()

    @staticmethod
    def __get_expense(date: datetime.date, cinema_id: int):
        return CashierService.__get_base_query(date, cinema_id).filter(Transaction.sum < 0).scalar()

    @staticmethod
    def __get_all_by_cash(date: datetime.date, cinema_id: int):
        return CashierService.__get_base_query(date, cinema_id) \
            .filter(Transaction.sum >= 0) \
            .filter(Transaction.transaction_type == TransactionTypeEnum.cash) \
            .scalar()

    @staticmethod
    def __get_all_by_card(date: datetime.date, cinema_id: int):
        return CashierService.__get_base_query(date, cinema_id) \
            .filter(Transaction.sum >= 0) \
            .filter(Transaction.transaction_type == TransactionTypeEnum.card) \
            .scalar()

    @staticmethod
    def __get_cashier_start_base_query(date: datetime.date, cinema_id: int):
        return db.session.query(func.sum(Transaction.sum)) \
            .join(Cinema) \
            .join(City) \
            .filter(Transaction.cinema_id == cinema_id) \
            .filter(Transaction.transaction_status == TransactionStatusEnum.completed) \
            .filter(text("""date(get_shift_date("transaction".created_at, city.timezone, 0)) < :target_date""")) \
            .filter(Transaction.transaction_type == TransactionTypeEnum.cash) \
            .params(target_date=date)

    @staticmethod
    def __get_cashier_start(date, cinema_id: int):
        all_income = CashierService.__get_cashier_start_base_query(date, cinema_id).filter(
            Transaction.sum >= 0).scalar()
        all_expense = CashierService.__get_cashier_start_base_query(date, cinema_id).filter(
            Transaction.sum < 0).scalar()

        return all_income + all_expense

    @staticmethod
    def get_cashier_info(date: datetime.date, cinema_id: int):
        income = CashierService.__get_income(date, cinema_id) or 0
        expense = CashierService.__get_expense(date, cinema_id) or 0
        proceeds = income + expense
        all_by_cash = CashierService.__get_all_by_cash(date, cinema_id) or 0
        all_by_card = CashierService.__get_all_by_card(date, cinema_id) or 0
        cashier_start = CashierService.__get_cashier_start(date, cinema_id) or 0
        cashier_end = cashier_start + expense + all_by_cash

        return {
            "income": income,
            "expense": expense,
            "proceeds": proceeds,
            "all_by_cash": all_by_cash,
            "all_by_card": all_by_card,
            "cashier_start": cashier_start,
            "cashier_end": cashier_end
        }
