"""transaction_id в таблицах связи транзакций приводит к String (как transaction.id) и индексирует владельца

Из-за INTEGER против VARCHAR SQLite не мог джойнить по PK transaction и на каждую
подгрузку Reservation.transactions сканировал всю таблицу транзакций (~50 мс на резерв).

Revision ID: f3a9c2e1b7d4
Revises: d782090b6c24
Create Date: 2026-10-07 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f3a9c2e1b7d4'
down_revision = 'd782090b6c24'
branch_labels = None
depends_on = None

TABLES = (('reservation_transaction_dict', 'reservation_id'), ('certificate_transaction_dict', 'certificate_id'))


def upgrade():
    for table, owner_column in TABLES:
        with op.batch_alter_table(table, schema=None) as batch_op:
            batch_op.alter_column('transaction_id', existing_type=sa.Integer(), type_=sa.String())

        # Вне batch: при пересоздании таблицы batch создаёт индекс дважды (index already exists)
        op.create_index(op.f(f'ix_{table}_{owner_column}'), table, [owner_column], unique=False)


def downgrade():
    for table, owner_column in TABLES:
        # Тип назад в INTEGER не возвращаем: alembic скопирует данные через CAST(... AS INTEGER),
        # shortuuid превратятся в 0 и упадут на UNIQUE(transaction_id). VARCHAR совместим со старым кодом.
        op.drop_index(op.f(f'ix_{table}_{owner_column}'), table_name=table)
