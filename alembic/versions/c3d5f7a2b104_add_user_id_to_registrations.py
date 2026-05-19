"""add user_id to section_registrations

Revision ID: c3d5f7a2b104
Revises: b2c4e8f1a901
Create Date: 2026-05-19 14:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'c3d5f7a2b104'
down_revision: Union[str, Sequence[str], None] = 'b2c4e8f1a901'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('section_registrations', sa.Column('user_id', sa.Uuid(), nullable=True))


def downgrade() -> None:
    op.drop_column('section_registrations', 'user_id')
