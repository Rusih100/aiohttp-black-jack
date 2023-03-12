"""Init database

Revision ID: fd08602b8a00
Revises: 
Create Date: 2023-03-12 13:34:45.825915

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = 'fd08602b8a00'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('admins',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('email', sa.String(length=64), nullable=False),
    sa.Column('password', sa.String(length=64), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_admins_email'), 'admins', ['email'], unique=True)
    op.create_table('chats',
    sa.Column('chat_id', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('chat_id')
    )
    op.create_table('users',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('vk_id', sa.Integer(), nullable=False),
    sa.Column('first_name', sa.Text(), nullable=False),
    sa.Column('last_name', sa.Text(), nullable=False),
    sa.Column('is_admin', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('user_id')
    )
    op.create_index(op.f('ix_users_vk_id'), 'users', ['vk_id'], unique=True)
    op.create_table('games',
    sa.Column('game_id', sa.Integer(), nullable=False),
    sa.Column('chat_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['chat_id'], ['chats.chat_id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('game_id')
    )
    op.create_index(op.f('ix_games_chat_id'), 'games', ['chat_id'], unique=False)
    op.create_table('players',
    sa.Column('player_id', sa.Integer(), nullable=False),
    sa.Column('game_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('is_finished', sa.Boolean(), nullable=False),
    sa.Column('cash', sa.Integer(), nullable=True),
    sa.Column('bet', sa.Integer(), nullable=True),
    sa.Column('hand', sa.JSON(), nullable=True),
    sa.ForeignKeyConstraint(['game_id'], ['games.game_id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ),
    sa.PrimaryKeyConstraint('player_id')
    )
    op.create_index(op.f('ix_players_game_id'), 'players', ['game_id'], unique=False)
    op.create_index(op.f('ix_players_user_id'), 'players', ['user_id'], unique=False)
    op.create_table('states',
    sa.Column('state_id', sa.Integer(), nullable=False),
    sa.Column('game_id', sa.Integer(), nullable=False),
    sa.Column('players_count', sa.Integer(), nullable=False),
    sa.Column('join_players_count', sa.Integer(), nullable=False),
    sa.Column('finished_players_count', sa.Integer(), nullable=False),
    sa.Column('type', sa.Enum('WAITING_NUMBER_OF_PLAYERS', 'INVITING_PLAYERS', 'PLAYERS_ARE_PLAYING', name='gamestates'), nullable=False),
    sa.ForeignKeyConstraint(['game_id'], ['games.game_id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('state_id')
    )
    op.create_index(op.f('ix_states_game_id'), 'states', ['game_id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_states_game_id'), table_name='states')
    op.drop_table('states')
    op.drop_index(op.f('ix_players_user_id'), table_name='players')
    op.drop_index(op.f('ix_players_game_id'), table_name='players')
    op.drop_table('players')
    op.drop_index(op.f('ix_games_chat_id'), table_name='games')
    op.drop_table('games')
    op.drop_index(op.f('ix_users_vk_id'), table_name='users')
    op.drop_table('users')
    op.drop_table('chats')
    op.drop_index(op.f('ix_admins_email'), table_name='admins')
    op.drop_table('admins')
    # ### end Alembic commands ###
