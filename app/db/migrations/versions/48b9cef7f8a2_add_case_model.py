"""Add case model

Revision ID: 48b9cef7f8a2
Revises: 2a0a7fdef0f6
Create Date: 2024-09-03 17:01:26.010768

"""

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = "48b9cef7f8a2"
down_revision: str = "2a0a7fdef0f6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "cases",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column("case_type", sa.Enum("CCQ", "CLA", name="casetypes"), nullable=False),
        sa.Column("assigned_to", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_cases_case_type"), "cases", ["case_type"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_cases_case_type"), table_name="cases")
    op.drop_table("cases")
