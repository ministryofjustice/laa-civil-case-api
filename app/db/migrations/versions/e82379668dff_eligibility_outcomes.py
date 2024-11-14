"""eligibility_outcomes

Revision ID: e82379668dff
Revises: da58faadfe41
Create Date: 2024-10-14 11:32:06.932807

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "e82379668dff"
down_revision: Union[str, None] = "dc7b04aafeff"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    sa.Enum("INSCOPE", "OUTOFSCOPE", "UNKNOWN", name="eligibilityoutcometype").create(
        op.get_bind()
    )
    sa.Enum("CCQ", "MEANS", "CFE", name="eligibilitytype").create(op.get_bind())
    op.create_table(
        "eligibility_outcomes",
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("case_id", sa.Uuid(), nullable=False),
        sa.Column(
            "eligibility_type",
            postgresql.ENUM(
                "CCQ", "MEANS", "CFE", name="eligibilitytype", create_type=False
            ),
            nullable=False,
        ),
        sa.Column(
            "outcome",
            postgresql.ENUM(
                "INSCOPE",
                "OUTOFSCOPE",
                "UNKNOWN",
                name="eligibilityoutcometype",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("answers", sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(
            ["case_id"],
            ["cases.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_eligibility_outcomes_case_id"),
        "eligibility_outcomes",
        ["case_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_eligibility_outcomes_eligibility_type"),
        "eligibility_outcomes",
        ["eligibility_type"],
        unique=False,
    )
    op.create_index(
        op.f("ix_eligibility_outcomes_outcome"),
        "eligibility_outcomes",
        ["outcome"],
        unique=False,
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(
        op.f("ix_eligibility_outcomes_outcome"), table_name="eligibility_outcomes"
    )
    op.drop_index(
        op.f("ix_eligibility_outcomes_eligibility_type"),
        table_name="eligibility_outcomes",
    )
    op.drop_index(
        op.f("ix_eligibility_outcomes_case_id"), table_name="eligibility_outcomes"
    )
    op.drop_table("eligibility_outcomes")
    sa.Enum("CCQ", "MEANS", "CFE", name="eligibilitytype").drop(op.get_bind())
    sa.Enum("INSCOPE", "OUTOFSCOPE", "UNKNOWN", name="eligibilityoutcometype").drop(
        op.get_bind()
    )
    # ### end Alembic commands ###