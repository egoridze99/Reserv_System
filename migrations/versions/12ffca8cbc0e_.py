"""empty message

Revision ID: 12ffca8cbc0e
Revises: ee1219dd368b
Create Date: 2024-01-19 17:43:06.182327

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '12ffca8cbc0e'
down_revision = 'ee1219dd368b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('certificate', schema=None) as batch_op:
        batch_op.add_column(sa.Column('created_at_datetime', sa.String(length=50), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('certificate', schema=None) as batch_op:
        batch_op.drop_column('created_at_datetime')

    # ### end Alembic commands ###
