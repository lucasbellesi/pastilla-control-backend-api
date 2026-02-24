"""Convert user role to enum

Revision ID: 20260224_02
Revises: 20260224_01
Create Date: 2026-02-24 00:10:00.000000
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "20260224_02"
down_revision: str | None = "20260224_01"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


user_role_enum = postgresql.ENUM("PATIENT", "CAREGIVER", "ADMIN", name="user_role")


def upgrade() -> None:
    op.execute(
        """
        UPDATE users
        SET role = 'PATIENT'
        WHERE role NOT IN ('PATIENT', 'CAREGIVER', 'ADMIN')
        """
    )

    user_role_enum.create(op.get_bind(), checkfirst=True)
    op.alter_column(
        "users",
        "role",
        existing_type=sa.String(length=30),
        type_=user_role_enum,
        existing_nullable=False,
        postgresql_using="role::user_role",
    )
    op.alter_column("users", "role", server_default="PATIENT")


def downgrade() -> None:
    op.alter_column(
        "users",
        "role",
        existing_type=user_role_enum,
        type_=sa.String(length=30),
        existing_nullable=False,
        postgresql_using="role::text",
    )
    op.alter_column("users", "role", server_default="PATIENT")
    user_role_enum.drop(op.get_bind(), checkfirst=True)
