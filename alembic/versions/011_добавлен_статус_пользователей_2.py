"""Добавлен статус пользователей 2

Revision ID: 011
Revises: 010
Create Date: 2024-07-15 22:31:46.062854

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils
from bot.db.models.users import Statuses


# revision identifiers, used by Alembic.
revision: str = '011'
down_revision: Union[str, None] = '010'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('users', 'status',
               existing_type=sa.VARCHAR(length=255),
               type_=sqlalchemy_utils.types.choice.ChoiceType(Statuses),
               existing_nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('users', 'status',
               existing_type=sqlalchemy_utils.types.choice.ChoiceType(),
               type_=sa.VARCHAR(length=255),
               existing_nullable=True)
    # ### end Alembic commands ###
