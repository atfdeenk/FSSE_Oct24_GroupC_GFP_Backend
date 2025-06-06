"""add voucher model and link to orders

Revision ID: 8836e224fd31
Revises: d435a85927d0
Create Date: 2025-05-09 22:32:32.860100

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8836e224fd31'
down_revision = 'd435a85927d0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('vouchers',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('code', sa.String(length=50), nullable=False),
    sa.Column('discount_percent', sa.Float(), nullable=True),
    sa.Column('discount_amount', sa.Numeric(precision=10, scale=2), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('expires_at', sa.DateTime(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('code')
    )
    with op.batch_alter_table('orders', schema=None) as batch_op:
        batch_op.add_column(sa.Column('voucher_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(None, 'vouchers', ['voucher_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('orders', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('voucher_id')

    op.drop_table('vouchers')
    # ### end Alembic commands ###
