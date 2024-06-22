"""Add username to User model

Revision ID: cdf4d644a77b
Revises: 6c62ca5ebbfc
Create Date: 2024-06-20 21:30:04.649122

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cdf4d644a77b'
down_revision = '6c62ca5ebbfc'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('username', sa.String(length=150), nullable=True))
        batch_op.create_unique_constraint('uq_user_username', ['username'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_constraint('uq_user_username', type_='unique')
        batch_op.drop_column('username')

    # ### end Alembic commands ###