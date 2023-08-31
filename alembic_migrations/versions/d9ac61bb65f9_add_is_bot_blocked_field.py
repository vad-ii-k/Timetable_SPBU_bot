"""add_is_bot_blocked_field

Revision ID: d9ac61bb65f9
Revises: b351ee68c259
Create Date: 2023-08-31 10:37:45.946370

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "d9ac61bb65f9"
down_revision = "b351ee68c259"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "user",
        sa.Column(
            "is_bot_blocked",
            sa.Boolean(),
            server_default=sa.sql.expression.false(),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column("user", "is_bot_blocked")
