"""Initial migration with two tables

Revision ID: 50e7b7f0acb7
Revises: 
Create Date: 2025-04-23 15:36:26.423870

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '50e7b7f0acb7'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('scraped_articles',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('url', sa.String(), nullable=False),
    sa.Column('domain', sa.String(), nullable=True),
    sa.Column('title', sa.String(), nullable=True),
    sa.Column('content', sa.Text(), nullable=True),
    sa.Column('scraped_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.Column('publication_date', sa.Date(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_scraped_articles_domain'), 'scraped_articles', ['domain'], unique=False)
    op.create_index(op.f('ix_scraped_articles_id'), 'scraped_articles', ['id'], unique=False)
    op.create_index(op.f('ix_scraped_articles_url'), 'scraped_articles', ['url'], unique=True)
    op.create_table('summaries',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('domain', sa.String(), nullable=True),
    sa.Column('language', sa.String(), nullable=True),
    sa.Column('date', sa.Date(), nullable=True),
    sa.Column('content', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_summaries_date'), 'summaries', ['date'], unique=False)
    op.create_index(op.f('ix_summaries_domain'), 'summaries', ['domain'], unique=False)
    op.create_index(op.f('ix_summaries_id'), 'summaries', ['id'], unique=False)
    op.create_index(op.f('ix_summaries_language'), 'summaries', ['language'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_summaries_language'), table_name='summaries')
    op.drop_index(op.f('ix_summaries_id'), table_name='summaries')
    op.drop_index(op.f('ix_summaries_domain'), table_name='summaries')
    op.drop_index(op.f('ix_summaries_date'), table_name='summaries')
    op.drop_table('summaries')
    op.drop_index(op.f('ix_scraped_articles_url'), table_name='scraped_articles')
    op.drop_index(op.f('ix_scraped_articles_id'), table_name='scraped_articles')
    op.drop_index(op.f('ix_scraped_articles_domain'), table_name='scraped_articles')
    op.drop_table('scraped_articles')
    # ### end Alembic commands ###
