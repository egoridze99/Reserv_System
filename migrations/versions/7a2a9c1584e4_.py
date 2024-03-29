"""empty message

Revision ID: 7a2a9c1584e4
Revises: 938d513711ac
Create Date: 2022-11-16 16:44:28.282081

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7a2a9c1584e4'
down_revision = '938d513711ac'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('certificate', schema=None) as batch_op:
        batch_op.create_unique_constraint(batch_op.f('uq_certificate_ident'), ['ident'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('certificate', schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f('uq_certificate_ident'), type_='unique')

    # ### end Alembic commands ###
