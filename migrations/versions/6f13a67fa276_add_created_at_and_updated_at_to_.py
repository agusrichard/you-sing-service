"""Add created_at and updated_at to Playlist model

Revision ID: 6f13a67fa276
Revises: 6c57fb94cc11
Create Date: 2022-05-25 17:42:22.958825

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6f13a67fa276'
down_revision = '6c57fb94cc11'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('playlists', sa.Column('created_at', sa.DateTime(), nullable=True))
    op.add_column('playlists', sa.Column('updated_at', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('playlists', 'updated_at')
    op.drop_column('playlists', 'created_at')
    # ### end Alembic commands ###