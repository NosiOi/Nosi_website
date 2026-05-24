"""Add name and category to meals

Revision ID: c65d064d047a
Revises: 8ccc72b53224
Create Date: 2026-05-24 17:51:54.633565

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c65d064d047a'
down_revision = '8ccc72b53224'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('meals', schema=None) as batch_op:
        batch_op.add_column(sa.Column('name', sa.String(length=120), nullable=True))
        batch_op.add_column(sa.Column('category', sa.String(length=50), nullable=True))
        batch_op.drop_column('is_daily_summary')

    op.execute("UPDATE meals SET name = 'Прийом їжі' WHERE name IS NULL")
    op.execute("UPDATE meals SET category = 'general' WHERE category IS NULL")

    with op.batch_alter_table('meals', schema=None) as batch_op:
        batch_op.alter_column('name', nullable=False)
        batch_op.alter_column('category', nullable=False)


    # ### end Alembic commands ###
