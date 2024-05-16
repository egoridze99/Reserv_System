from models import TransactionTypeEnum, TransactionStatusEnum


def get_money_query(area, until, till, is_income):
    def get_transactions_by_type(type: 'TransactionTypeEnum'):
        return f"""select sum from "transaction" where id = t.id and transaction_type = '{type}' and {'sum > 0' if is_income else 'sum < 0'}"""

    return f""" select 
                    area, 
                    card, 
                    cash, 
                    sbp, 
                    (ifnull(card, 0) + ifnull(cash, 0) + ifnull(sbp, 0)) as sum from (
                        select 
                            name as area, 
                            sum(card) as card, 
                            sum(cash) as cash,
                            sum(sbp) as sbp from
                                (select
                                    {area}.id,
                                    {area}.name,
                                    ({get_transactions_by_type(TransactionTypeEnum.card.value)}) as card,
                                    ({get_transactions_by_type(TransactionTypeEnum.cash.value)}) as cash,
                                    ({get_transactions_by_type(TransactionTypeEnum.sbp.value)}) as sbp
                                from
                                    "transaction" t
                                left join cinema on cinema.id = t.cinema_id
                                left join
                                    reservation_transaction_dict rtd on rtd.transaction_id = t.id
                                left join
                                    reservation on rtd.reservation_id = reservation.id
        
                                left join room on room.id = reservation.room_id
                                where
                                    t.created_at between '{until}' and '{till}' and
                                    t.transaction_status = '{TransactionStatusEnum.completed.value}') 
                        group by id);
"""
