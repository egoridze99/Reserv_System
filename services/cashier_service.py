from datetime import datetime

from sqlalchemy import func, text, case

from db import db
from models import Transaction, Cinema, City, TransactionStatusEnum, TransactionTypeEnum


class CashierService:
    @staticmethod
    def __get_base_query(date: datetime.date, cinema_id: int):
        subquery = (
            db.session.query(
                func.sum(Transaction.sum).label("total_sum"),
                func.sum(
                    case([(Transaction.sum >= 0, Transaction.sum)], else_=0)
                ).label("income_sum"),
                func.sum(
                    case([(Transaction.sum < 0, Transaction.sum)], else_=0)
                ).label("expense_sum"),
                func.sum(
                    case([(Transaction.sum >= 0,
                           case([(Transaction.transaction_type == TransactionTypeEnum.cash, Transaction.sum)],
                                else_=0))], else_=0)
                ).label("cash_sum"),
                func.sum(
                    case([(Transaction.sum >= 0,
                           case([(Transaction.transaction_type == TransactionTypeEnum.card, Transaction.sum)],
                                else_=0))], else_=0)
                ).label("card_sum")
            )
            .join(Cinema)
            .join(City)
            .filter(Transaction.cinema_id == cinema_id)
            .filter(Transaction.transaction_status == TransactionStatusEnum.completed)
            .filter(text("""date(get_shift_date("transaction".created_at, city.timezone, 0)) = :target_date"""))
            .params(target_date=date)
            .subquery()
        )

        return db.session.query(subquery.c.total_sum, subquery.c.income_sum, subquery.c.expense_sum,
                                subquery.c.cash_sum, subquery.c.card_sum)

    @staticmethod
    def __get_cashier_start_base_query(date: datetime.date, cinema_id: int):
        return db.session.query(
            func.sum(Transaction.sum)
        ) \
            .join(Cinema) \
            .join(City) \
            .filter(Transaction.cinema_id == cinema_id) \
            .filter(Transaction.transaction_status == TransactionStatusEnum.completed) \
            .filter(text("""date(get_shift_date("transaction".created_at, city.timezone, 0)) < :target_date""")) \
            .filter(Transaction.transaction_type == TransactionTypeEnum.cash) \
            .params(target_date=date)

    @staticmethod
    def get_cashier_info(date: datetime.date, cinema_id: int):
        base_data = CashierService.__get_base_query(date, cinema_id).first()
        cashier_start_income = CashierService.__get_cashier_start_base_query(date, cinema_id).filter(
            Transaction.sum >= 0).scalar() or 0
        cashier_start_expense = CashierService.__get_cashier_start_base_query(date, cinema_id).filter(
            Transaction.sum < 0).scalar() or 0

        income = base_data.income_sum or 0
        expense = base_data.expense_sum or 0
        proceeds = income + expense
        all_by_cash = base_data.cash_sum or 0
        all_by_card = base_data.card_sum or 0
        cashier_start = cashier_start_income + cashier_start_expense
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
