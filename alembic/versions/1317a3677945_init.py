"""Init

Revision ID: 1317a3677945
Revises: 
Create Date: 2023-02-22 18:18:58.253853

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = '1317a3677945'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('admins',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('email', sa.String(length=64), nullable=False),
    sa.Column('password', sa.String(length=64), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_admins_email'), 'admins', ['email'], unique=True)


def downgrade() -> None:
    op.drop_index(op.f('ix_admins_email'), table_name='admins')
    op.drop_table('admins')

