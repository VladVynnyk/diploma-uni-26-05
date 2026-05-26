"""Add admin role and consultation request fields

Revision ID: b4f57f9a0c31
Revises: a1f6cbb7c9c2
Create Date: 2026-05-24 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "b4f57f9a0c31"
down_revision = "a1f6cbb7c9c2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("is_admin", sa.Boolean(), nullable=False, server_default=sa.false()))

    op.add_column("order", sa.Column("topic", sa.String(length=255), nullable=True))
    op.add_column("order", sa.Column("message", sa.String(length=1000), nullable=True))
    op.add_column("order", sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("order", sa.Column("duration_minutes", sa.Integer(), nullable=False, server_default="60"))

    op.alter_column("order", "status", existing_type=sa.String(length=30), nullable=False, server_default="new")

    op.execute("UPDATE \"order\" SET status = 'new' WHERE status IS NULL OR status = 'Unpaid'")
    op.execute("UPDATE \"order\" SET status = 'confirmed' WHERE status = 'Paid'")


def downgrade() -> None:
    op.execute("UPDATE \"order\" SET status = 'Paid' WHERE status IN ('confirmed', 'in_progress', 'completed')")
    op.execute("UPDATE \"order\" SET status = 'Unpaid' WHERE status IN ('new', 'cancelled') OR status IS NULL")

    op.alter_column("order", "status", existing_type=sa.String(length=30), nullable=True, server_default=None)
    op.drop_column("order", "duration_minutes")
    op.drop_column("order", "scheduled_at")
    op.drop_column("order", "message")
    op.drop_column("order", "topic")
    op.drop_column("users", "is_admin")
