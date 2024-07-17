"""short описание

Revision ID: 016
Revises: 015
Create Date: 2024-07-16 18:21:25.492411

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '016'
down_revision: Union[str, None] = '015'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('faqs',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('text', sa.Text(), nullable=False),
    sa.Column('short_description', sa.String(), nullable=False),
    sa.Column('document', sa.String(), nullable=True),
    sa.Column('display_in_keyboard', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('faqs')
    # ### end Alembic commands ###
