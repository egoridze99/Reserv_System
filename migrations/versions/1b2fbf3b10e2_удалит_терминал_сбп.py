"""Удалит терминал сбп

Revision ID: 1b2fbf3b10e2
Revises: 37eb6b94d763
Create Date: 2026-07-08 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '1b2fbf3b10e2'
down_revision = '37eb6b94d763'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('cinema', schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f('fk_cinema_sbp_terminal_id_sbp_terminal'), type_='foreignkey')
        batch_op.drop_column('sbp_terminal_id')

    op.drop_table('sbp_terminal')


def downgrade():
    op.create_table('sbp_terminal',
                    sa.Column('id', sa.String(), nullable=False),
                    sa.PrimaryKeyConstraint('id', name=op.f('pk_sbp_terminal'))
                    )
    with op.batch_alter_table('cinema', schema=None) as batch_op:
        batch_op.add_column(sa.Column('sbp_terminal_id', sa.String(), nullable=True))
        batch_op.create_foreign_key(batch_op.f('fk_cinema_sbp_terminal_id_sbp_terminal'), 'sbp_terminal',
                                    ['sbp_terminal_id'], ['id'])
