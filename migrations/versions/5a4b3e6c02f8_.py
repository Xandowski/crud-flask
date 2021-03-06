"""empty message

Revision ID: 5a4b3e6c02f8
Revises: c01493eff63e
Create Date: 2022-04-12 22:39:31.032322

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5a4b3e6c02f8'
down_revision = 'c01493eff63e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('task', 'name',
               existing_type=sa.VARCHAR(length=150),
               nullable=False)
    op.create_unique_constraint(None, 'user', ['email'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'user', type_='unique')
    op.alter_column('task', 'name',
               existing_type=sa.VARCHAR(length=150),
               nullable=True)
    # ### end Alembic commands ###
