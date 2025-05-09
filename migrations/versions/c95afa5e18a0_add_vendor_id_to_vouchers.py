"""add vendor_id to vouchers

Revision ID: c95afa5e18a0
Revises: da19eb1c0e80
Create Date: 2025-05-09 17:46:43

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c95afa5e18a0'
down_revision = 'da19eb1c0e80'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("vouchers", schema=None) as batch_op:
        batch_op.add_column(sa.Column("vendor_id", sa.Integer(), nullable=True))
    op.execute("UPDATE vouchers SET vendor_id = 1")
    with op.batch_alter_table("vouchers", schema=None) as batch_op:
        batch_op.alter_column("vendor_id", nullable=False)
        batch_op.create_foreign_key("fk_vouchers_vendor_id_users", "users", ["vendor_id"], ["id"])


def downgrade():
    with op.batch_alter_table("vouchers", schema=None) as batch_op:
        batch_op.drop_constraint("fk_vouchers_vendor_id_users", type_="foreignkey")
        batch_op.drop_column("vendor_id")
