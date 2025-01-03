"""case_tracker

Revision ID: 117a6ec2770b
Revises: da58faadfe41
Create Date: 2024-10-16 08:59:53.139922

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = "117a6ec2770b"
down_revision: Union[str, None] = "e82379668dff"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "case_tracker",
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("case_id", sa.Uuid(), nullable=False),
        sa.Column("gtm_anon_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("journey", sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(
            ["case_id"],
            ["cases.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_case_tracker_case_id"), "case_tracker", ["case_id"], unique=False
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_case_tracker_case_id"), table_name="case_tracker")
    op.drop_table("case_tracker")
    # ### end Alembic commands ###
