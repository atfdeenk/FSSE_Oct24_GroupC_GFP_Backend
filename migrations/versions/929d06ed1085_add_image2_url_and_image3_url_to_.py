"""Add image2_url and image3_url to ProductImages

Revision ID: 929d06ed1085
Revises: a52fcdbd7deb
Create Date: 2025-04-23 20:50:18.391601

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '929d06ed1085'
down_revision = 'a52fcdbd7deb'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('images', schema=None) as batch_op:
        batch_op.add_column(sa.Column('image2_url', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('image3_url', sa.Text(), nullable=True))
        batch_op.drop_column('image1_ur2')
        batch_op.drop_column('image1_ur3')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('images', schema=None) as batch_op:
        batch_op.add_column(sa.Column('image1_ur3', sa.TEXT(), nullable=True))
        batch_op.add_column(sa.Column('image1_ur2', sa.TEXT(), nullable=True))
        batch_op.drop_column('image3_url')
        batch_op.drop_column('image2_url')

    # ### end Alembic commands ###
