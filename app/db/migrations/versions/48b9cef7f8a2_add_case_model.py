"""Add case model

Revision ID: 48b9cef7f8a2
Revises: 2a0a7fdef0f6
Create Date: 2024-10-03 22:49:21.553826

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "48b9cef7f8a2"
down_revision: Union[str, None] = "2a0a7fdef0f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    sa.Enum("CCQ", "CLA", name="casetypes").create(op.get_bind())
    op.create_table(
        "cases",
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "case_type",
            postgresql.ENUM("CCQ", "CLA", name="casetypes", create_type=False),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_cases_case_type"), "cases", ["case_type"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_cases_case_type"), table_name="cases")
    op.drop_table("cases")
    sa.Enum("CCQ", "CLA", name="casetypes").drop(op.get_bind())
