"""Rename user table to users

Revision ID: a1f6cbb7c9c2
Revises: 9936a6ff0083
Create Date: 2026-05-23 20:10:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "a1f6cbb7c9c2"
down_revision = "9936a6ff0083"
branch_labels = None
depends_on = None


FOREIGN_KEYS = {
    "order": [
        "order_client_id_fkey",
        "order_consultant_id_fkey",
    ],
    "review": [
        "review_client_id_fkey",
        "review_consultant_id_fkey",
    ],
    "tags_users": [
        "tags_users_user_id_fkey",
    ],
}


def _drop_foreign_key_if_exists(table_name: str, constraint_name: str) -> None:
    inspector = sa.inspect(op.get_bind())
    foreign_keys = inspector.get_foreign_keys(table_name)

    if any(fk["name"] == constraint_name for fk in foreign_keys):
        op.drop_constraint(constraint_name, table_name, type_="foreignkey")


def _create_foreign_keys(target_table: str) -> None:
    op.create_foreign_key(
        "order_client_id_fkey",
        "order",
        target_table,
        ["client_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "order_consultant_id_fkey",
        "order",
        target_table,
        ["consultant_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "review_client_id_fkey",
        "review",
        target_table,
        ["client_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "review_consultant_id_fkey",
        "review",
        target_table,
        ["consultant_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "tags_users_user_id_fkey",
        "tags_users",
        target_table,
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = set(inspector.get_table_names())

    if "user" not in tables or "users" in tables:
        return

    for table_name, constraints in FOREIGN_KEYS.items():
        for constraint_name in constraints:
            _drop_foreign_key_if_exists(table_name, constraint_name)

    op.rename_table("user", "users")
    _create_foreign_keys("users")


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = set(inspector.get_table_names())

    if "users" not in tables or "user" in tables:
        return

    for table_name, constraints in FOREIGN_KEYS.items():
        for constraint_name in constraints:
            _drop_foreign_key_if_exists(table_name, constraint_name)

    op.rename_table("users", "user")
    _create_foreign_keys("user")
