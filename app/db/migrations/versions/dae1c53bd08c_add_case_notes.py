"""Add case notes

Revision ID: dae1c53bd08c
Revises: 48b9cef7f8a2
Create Date: 2024-10-03 22:52:44.677974

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "dae1c53bd08c"
down_revision: Union[str, None] = "48b9cef7f8a2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    sa.Enum(
        "personal", "provider", "caseworker", "operator", "other", name="notetype"
    ).create(op.get_bind())
    op.create_table(
        "case_notes",
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "note_type",
            postgresql.ENUM(
                "personal",
                "provider",
                "caseworker",
                "operator",
                "other",
                name="notetype",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("content", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("case_id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(
            ["case_id"],
            ["cases.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_case_notes_note_type"), "case_notes", ["note_type"], unique=False
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_case_notes_note_type"), table_name="case_notes")
    op.drop_table("case_notes")
    sa.Enum(
        "personal", "provider", "caseworker", "operator", "other", name="notetype"
    ).drop(op.get_bind())
