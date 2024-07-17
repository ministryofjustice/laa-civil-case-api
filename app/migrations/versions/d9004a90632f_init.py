"""init

Revision ID: d9004a90632f
Revises: 
Create Date: 2024-07-17 22:19:10.309924

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'd9004a90632f'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('case',
    sa.Column('category', sa.Enum('aap', 'med', 'com', 'crm', 'deb', 'disc', 'edu', 'mat', 'fmed', 'hou', 'immas', 'mhe', 'pl', 'pub', 'wb', 'mosl', 'hlpas', name='categories'), nullable=False),
    sa.Column('name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('time', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_case_category'), 'case', ['category'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_case_category'), table_name='case')
    op.drop_table('case')
    # ### end Alembic commands ###
