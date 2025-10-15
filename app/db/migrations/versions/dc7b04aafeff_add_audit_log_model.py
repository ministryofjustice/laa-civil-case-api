"""Add audit log model

Revision ID: dc7b04aafeff
Revises: da58faadfe41
Create Date: 2024-10-09 20:53:03.130872

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "dc7b04aafeff"
down_revision: Union[str, None] = "da58faadfe41"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    sa.Enum(
        "case_created",
        "case_updated",
        "case_deleted",
        "user_authenticated",
        "user_wrong_password",
        "error",
        "other",
        name="eventtype",
    ).create(op.get_bind())
    op.create_table(
        "audit_log",
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "event_type",
            postgresql.ENUM(
                "case_created",
                "case_updated",
                "case_deleted",
                "user_authenticated",
                "user_wrong_password",
                "error",
                "other",
                name="eventtype",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("username", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("case_id", sa.Uuid(), nullable=True),
        sa.ForeignKeyConstraint(
            ["case_id"],
            ["cases.id"],
        ),
        sa.ForeignKeyConstraint(
            ["username"],
            ["users.username"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_audit_log_case_id"), "audit_log", ["case_id"], unique=False
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_audit_log_case_id"), table_name="audit_log")
    op.drop_table("audit_log")
    sa.Enum(
        "case_created",
        "case_updated",
        "case_deleted",
        "user_authenticated",
        "user_wrong_password",
        "error",
        "other",
        name="eventtype",
    ).drop(op.get_bind())
