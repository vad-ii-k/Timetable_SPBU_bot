"""Init

Revision ID: b351ee68c259
Revises: 
Create Date: 2023-02-22 12:07:18.715553

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "b351ee68c259"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    group_id_seq = sa.Sequence("group_id_seq")
    op.execute(sa.sql.ddl.CreateSequence(group_id_seq))
    op.create_table(
        "group",
        sa.Column("group_id", sa.Integer(), group_id_seq, primary_key=True, nullable=False),
        sa.Column("tt_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False),
    )
    op.create_index("group_idx_name", "group", ["name"], unique=False)

    user_id_seq = sa.Sequence("user_id_seq")
    op.execute(sa.sql.ddl.CreateSequence(user_id_seq))
    op.create_table(
        "user",
        sa.Column("user_id", sa.Integer(), user_id_seq, primary_key=True, nullable=False),
        sa.Column("tg_id", sa.BigInteger(), nullable=False),
        sa.Column("full_name", sa.String(length=100), nullable=False),
        sa.Column("username", sa.String(length=50), nullable=True),
        sa.Column("start_date", sa.Date(), server_default=sa.func.current_date(), nullable=False),
    )

    op.create_table(
        "main_schedule_info",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("timetable_id", sa.Integer(), nullable=False),
        sa.Column("user_type_is_student", sa.Boolean(), nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.ForeignKeyConstraint(
            ("user_id",),
            ["user.user_id"],
        ),
    )
    op.create_index("main_schedule_info_idx_user_id", "main_schedule_info", ["user_id"], unique=True)

    settings_id_seq = sa.Sequence("settings_id_seq")
    op.execute(sa.sql.ddl.CreateSequence(settings_id_seq))
    op.create_table(
        "settings",
        sa.Column("settings_id", sa.Integer(), settings_id_seq, primary_key=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("daily_summary", sa.Time(), nullable=True),
        sa.Column("notification_of_lesson", sa.Time(), nullable=True),
        sa.Column(
            "schedule_view_is_picture",
            sa.Boolean(),
            server_default=sa.sql.expression.false(),
            nullable=False,
        ),
        sa.Column("language", sa.String(length=2), nullable=False),
        sa.ForeignKeyConstraint(
            ("user_id",),
            ["user.user_id"],
        ),
    )


def downgrade() -> None:
    op.drop_table("settings")
    op.execute(sa.sql.ddl.DropSequence(sa.Sequence("settings_id_seq")))
    op.drop_index("main_schedule_info_idx_user_id", table_name="main_schedule_info")
    op.drop_table("main_schedule_info")
    op.drop_table("user")
    op.execute(sa.sql.ddl.DropSequence(sa.Sequence("user_id_seq")))
    op.drop_index("group_idx_name", table_name="group")
    op.drop_table("group")
    op.execute(sa.sql.ddl.DropSequence(sa.Sequence("group_id_seq")))
