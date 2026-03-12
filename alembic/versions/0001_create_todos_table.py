"""create todos table

Revision ID: 0001
Revises:
Create Date: 2026-03-12

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "todos",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.String(1000), nullable=True),
        sa.Column("completed", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("priority", sa.Integer(), nullable=False, server_default=sa.text("1")),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column("user_id", sa.String(255), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_todos_id", "todos", ["id"])
    op.create_index("ix_todos_title", "todos", ["title"])
    op.create_index("ix_todos_user_id", "todos", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_todos_user_id", table_name="todos")
    op.drop_index("ix_todos_title", table_name="todos")
    op.drop_index("ix_todos_id", table_name="todos")
    op.drop_table("todos")
