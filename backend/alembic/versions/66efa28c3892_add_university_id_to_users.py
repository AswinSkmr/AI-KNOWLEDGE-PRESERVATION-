"""add university_id to users

Revision ID: 66efa28c3892
Revises: 8756a1098ee2
Create Date: 2026-07-31 00:52:55.069193

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '66efa28c3892'
down_revision: Union[str, Sequence[str], None] = '8756a1098ee2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("university_id", sa.String(length=50), nullable=True))

    op.execute(
        "UPDATE users SET university_id = 'LEGACY-' || substr(id::text, 1, 8) "
        "WHERE university_id IS NULL"
    )

    op.alter_column("users", "university_id", nullable=False)

    op.create_unique_constraint("uq_users_university_id", "users", ["university_id"])


def downgrade() -> None:
    op.drop_constraint("uq_users_university_id", "users", type_="unique")
    op.drop_column("users", "university_id")
