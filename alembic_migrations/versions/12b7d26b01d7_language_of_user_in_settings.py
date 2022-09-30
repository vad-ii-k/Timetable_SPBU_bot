"""language of user in settings

Revision ID: 12b7d26b01d7
Revises:
Create Date: 2022-09-28 19:12:54.227874

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '12b7d26b01d7'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('settings', sa.Column('language', sa.String(length=2), nullable=True))
    op.execute('UPDATE settings SET language = (SELECT language FROM "user" WHERE user_id = settings.user_id);')
    op.drop_column('user', 'language')


def downgrade() -> None:
    op.add_column('user', sa.Column('language', sa.VARCHAR(length=10), nullable=True))
    op.execute('UPDATE "user" SET language = (SELECT language FROM settings WHERE user_id = "user".user_id);')
    op.drop_column('settings', 'language')
