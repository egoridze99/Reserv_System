"""empty message

Revision ID: cdede9c4d9cd
Revises: 12ffca8cbc0e
Create Date: 2024-01-19 17:44:22.333582

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cdede9c4d9cd'
down_revision = '12ffca8cbc0e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('certificate', schema=None) as batch_op:
        batch_op.drop_column('created_at')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('certificate', schema=None) as batch_op:
        batch_op.add_column(sa.Column('created_at', sa.VARCHAR(length=50), nullable=True))

    # ### end Alembic commands ###