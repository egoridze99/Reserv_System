"""Initial migration

Revision ID: adbbf50841c9
Revises: 
Create Date: 2022-10-25 18:15:08.551035

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'adbbf50841c9'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('checkout', schema=None) as batch_op:
        batch_op.alter_column('sum',
               existing_type=sa.INTEGER(),
               nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('checkout', schema=None) as batch_op:
        batch_op.alter_column('sum',
               existing_type=sa.INTEGER(),
               nullable=False)

    # ### end Alembic commands ###
