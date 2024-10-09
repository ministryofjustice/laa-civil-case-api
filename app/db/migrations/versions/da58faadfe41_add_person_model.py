"""Add person model

Revision ID: da58faadfe41
Revises: dae1c53bd08c
Create Date: 2024-10-04 19:59:31.533189

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = "da58faadfe41"
down_revision: Union[str, None] = "dae1c53bd08c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "persons",
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("case_id", sa.Uuid(), nullable=False),
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("address", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("phone_number", sa.String(), nullable=True),
        sa.Column("postcode", sa.String(), nullable=True),
        sa.Column("email", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(
            ["case_id"],
            ["cases.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_persons_case_id"), "persons", ["case_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_persons_case_id"), table_name="persons")
    op.drop_table("persons")
