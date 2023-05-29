"""add foreign-key

Revision ID: 21661ae09865
Revises: 80998c210c46
Create Date: 2023-05-28 23:44:10.253392

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '21661ae09865'
down_revision = '80998c210c46'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('posts', sa.Column('owner_id', sa.Integer(), nullable=False))
    op.create_foreign_key('post_users_fk', source_table='posts', referent_table='users',
                          local_cols=['owner_id'], remote_cols=['id'], ondelete='CASCADE')
    pass


def downgrade() -> None:
    op.drop_constraint('post_users_fk', table_name='posts')
    op.drop_column('posts', 'owner_id')
    pass
