"""empty message

Revision ID: f2032c57070f
Revises: e1ccf1856e42
Create Date: 2024-01-19 17:51:37.551612

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f2032c57070f'
down_revision = 'e1ccf1856e42'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('reservation_queue', schema=None) as batch_op:
        batch_op.add_column(sa.Column('created_at_datetime', sa.DateTime(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('reservation_queue', schema=None) as batch_op:
        batch_op.drop_column('created_at_datetime')

    # ### end Alembic commands ###
