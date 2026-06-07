"""add onboarding models: user_profiles, user_training_goals, injuries, user_injuries

Revision ID: onboarding_0001
Revises: 3332181752e7
Create Date: 2026-06-07 08:55:00
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'onboarding_0001'
down_revision = '3332181752e7'
branch_labels = None
depends_on = None


def upgrade():
    # USER PROFILES
    op.create_table(
        'user_profiles',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey("users.id"), nullable=False, unique=True),
        sa.Column('training_location', sa.String(length=32), nullable=False),
        sa.Column('wants_nutrition', sa.Boolean(), default=False),
        sa.Column('wants_recovery', sa.Boolean(), default=False),
        sa.Column('onboarding_completed', sa.Boolean(), default=False)
    )

    # USER TRAINING GOALS
    op.create_table(
        'user_training_goals',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey("users.id"), nullable=False, unique=True),
        sa.Column('primary_goal', sa.String(length=32), nullable=False),
        sa.Column('focus_upper', sa.Integer(), default=5),
        sa.Column('focus_lower', sa.Integer(), default=5),
        sa.Column('focus_core', sa.Integer(), default=5)
    )

    # INJURIES
    op.create_table(
        'injuries',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(length=128), nullable=False),
        sa.Column('description', sa.Text())
    )

    # USER INJURIES
    op.create_table(
        'user_injuries',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column('injury_id', sa.Integer(), sa.ForeignKey("injuries.id"), nullable=False),
        sa.Column('notes', sa.String(length=256))
    )


def downgrade():
    op.drop_table('user_injuries')
    op.drop_table('injuries')
    op.drop_table('user_training_goals')
    op.drop_table('user_profiles')
