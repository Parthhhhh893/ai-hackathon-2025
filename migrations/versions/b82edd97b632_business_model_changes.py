"""business model changes

Revision ID: b82edd97b632
Revises: 20250417_init
Create Date: 2025-04-17 10:20:15.741412

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b82edd97b632'
down_revision: Union[str, None] = '20250417_init'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
