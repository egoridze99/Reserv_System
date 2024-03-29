"""empty message

Revision ID: 5357cebb38e7
Revises: f4fcd1bddfa6
Create Date: 2023-04-20 12:01:54.186653

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5357cebb38e7'
down_revision = 'f4fcd1bddfa6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('reservation_queue', schema=None) as batch_op:
        batch_op.add_column(sa.Column('author_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('created_at', sa.String(length=50), nullable=True))
        batch_op.create_foreign_key('author_id', 'user', ['author_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('reservation_queue', schema=None) as batch_op:
        batch_op.drop_constraint('author_id', type_='foreignkey')
        batch_op.drop_column('created_at')
        batch_op.drop_column('author_id')

    # ### end Alembic commands ###
