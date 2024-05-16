"""empty message

Revision ID: 0662d67b0e4c
Revises: 5e229b3f7338
Create Date: 2024-04-19 13:28:42.364798

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0662d67b0e4c'
down_revision = '5e229b3f7338'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('guest_comment', schema=None) as batch_op:
        batch_op.add_column(sa.Column('author_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('created_at', sa.DateTime(), nullable=True))
        batch_op.create_foreign_key('author_id', 'user', ['author_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('guest_comment', schema=None) as batch_op:
        batch_op.drop_constraint('author_id', type_='foreignkey')
        batch_op.drop_column('created_at')
        batch_op.drop_column('author_id')

    # ### end Alembic commands ###