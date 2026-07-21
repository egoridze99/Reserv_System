"""Материализует end_date у резерва и добавляет индексы на FK лог-таблиц

Revision ID: 11065661ad0e
Revises: 1b2fbf3b10e2
Create Date: 2026-07-21 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '11065661ad0e'
down_revision = '1b2fbf3b10e2'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('reservation', schema=None) as batch_op:
        batch_op.add_column(sa.Column('end_date', sa.DateTime(), nullable=True))

    op.execute(
        "UPDATE reservation SET end_date = datetime(date, '+' || CAST(duration AS TEXT) || ' hours')"
    )

    with op.batch_alter_table('reservation', schema=None) as batch_op:
        batch_op.alter_column('end_date', nullable=False)
        batch_op.create_index(batch_op.f('ix_reservation_end_date'), ['end_date'], unique=False)

    with op.batch_alter_table('update_logs', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_update_logs_reservation_id'), ['reservation_id'], unique=False)

    with op.batch_alter_table('transaction_changes_log', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_transaction_changes_log_transaction_id'), ['transaction_id'],
                              unique=False)

    with op.batch_alter_table('guest_changes_logs', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_guest_changes_logs_guest_id'), ['guest_id'], unique=False)


def downgrade():
    with op.batch_alter_table('guest_changes_logs', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_guest_changes_logs_guest_id'))

    with op.batch_alter_table('transaction_changes_log', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_transaction_changes_log_transaction_id'))

    with op.batch_alter_table('update_logs', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_update_logs_reservation_id'))

    with op.batch_alter_table('reservation', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_reservation_end_date'))
        batch_op.drop_column('end_date')
