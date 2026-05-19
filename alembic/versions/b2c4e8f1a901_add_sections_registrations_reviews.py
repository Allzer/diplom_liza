"""add sections registrations reviews

Revision ID: b2c4e8f1a901
Revises: 6106fc0b3878
Create Date: 2026-05-19 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'b2c4e8f1a901'
down_revision: Union[str, Sequence[str], None] = '6106fc0b3878'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'sport_sections',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('title', sa.String(length=120), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('schedule', sa.String(length=200), nullable=False),
        sa.Column('trainer', sa.String(length=120), nullable=False),
        sa.Column('age_group', sa.String(length=80), nullable=False),
        sa.Column('price', sa.String(length=60), nullable=False),
        sa.Column('image_key', sa.String(length=40), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table(
        'section_registrations',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('section_id', sa.Integer(), nullable=False),
        sa.Column('last_name', sa.TEXT(), nullable=False),
        sa.Column('first_name', sa.TEXT(), nullable=False),
        sa.Column('patronymic', sa.TEXT(), nullable=True),
        sa.Column('phone_number', sa.String(length=17), nullable=False),
        sa.Column('email', sa.String(length=80), nullable=True),
        sa.Column('birth_date', sa.String(length=20), nullable=False),
        sa.Column('comment', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('created_at', sa.String(length=30), nullable=False),
        sa.ForeignKeyConstraint(['section_id'], ['sport_sections.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table(
        'reviews',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('author_name', sa.String(length=120), nullable=False),
        sa.Column('section_title', sa.String(length=120), nullable=True),
        sa.Column('rating', sa.Integer(), nullable=False),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('created_at', sa.String(length=30), nullable=False),
        sa.Column('is_published', sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade() -> None:
    op.drop_table('reviews')
    op.drop_table('section_registrations')
    op.drop_table('sport_sections')
