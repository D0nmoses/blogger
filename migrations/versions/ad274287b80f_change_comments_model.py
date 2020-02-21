"""Change comments model

Revision ID: ad274287b80f
Revises: d224c5d59d79
Create Date: 2020-02-21 11:51:11.277866

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'ad274287b80f'
down_revision = 'd224c5d59d79'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('comments', sa.Column('comment_content', sa.String(), nullable=True))
    op.add_column('comments', sa.Column('user_id', sa.Integer(), nullable=True))
    op.drop_index('ix_comments_timestamp', table_name='comments')
    op.drop_constraint('comments_post_id_fkey', 'comments', type_='foreignkey')
    op.drop_constraint('comments_author_id_fkey', 'comments', type_='foreignkey')
    op.create_foreign_key(None, 'comments', 'posts', ['post_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'comments', 'users', ['user_id'], ['id'])
    op.drop_column('comments', 'author_id')
    op.drop_column('comments', 'body')
    op.drop_column('comments', 'timestamp')
    op.drop_column('comments', 'disabled')
    op.drop_column('comments', 'body_html')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('comments', sa.Column('body_html', sa.TEXT(), autoincrement=False, nullable=True))
    op.add_column('comments', sa.Column('disabled', sa.BOOLEAN(), autoincrement=False, nullable=True))
    op.add_column('comments', sa.Column('timestamp', postgresql.TIMESTAMP(), autoincrement=False, nullable=True))
    op.add_column('comments', sa.Column('body', sa.TEXT(), autoincrement=False, nullable=True))
    op.add_column('comments', sa.Column('author_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'comments', type_='foreignkey')
    op.drop_constraint(None, 'comments', type_='foreignkey')
    op.create_foreign_key('comments_author_id_fkey', 'comments', 'users', ['author_id'], ['id'])
    op.create_foreign_key('comments_post_id_fkey', 'comments', 'posts', ['post_id'], ['id'])
    op.create_index('ix_comments_timestamp', 'comments', ['timestamp'], unique=False)
    op.drop_column('comments', 'user_id')
    op.drop_column('comments', 'comment_content')
    # ### end Alembic commands ###
