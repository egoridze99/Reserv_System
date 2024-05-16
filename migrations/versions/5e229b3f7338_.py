"""empty message

Revision ID: 5e229b3f7338
Revises: 07fa70431171
Create Date: 2024-04-18 16:37:00.394334

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5e229b3f7338'
down_revision = '07fa70431171'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('guest_comment',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('text', sa.Text(), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_guest_comment'))
    )
    op.create_table('guest_comment_dict',
    sa.Column('comment_id', sa.Integer(), nullable=True),
    sa.Column('guest_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['comment_id'], ['guest_comment.id'], name='comment_id'),
    sa.ForeignKeyConstraint(['guest_id'], ['guest.id'], name='guest_id'),
    sa.UniqueConstraint('comment_id', name=op.f('uq_guest_comment_dict_comment_id'))
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('guest_comment_dict')
    op.drop_table('guest_comment')
    # ### end Alembic commands ###