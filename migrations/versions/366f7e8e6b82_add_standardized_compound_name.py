"""Add standardized compound name

Revision ID: 366f7e8e6b82
Revises: a15e67cf35fe
Create Date: 2019-03-07 16:40:54.005873

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '366f7e8e6b82'
down_revision = 'a15e67cf35fe'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('compound', schema=None) as batch_op:
        batch_op.add_column(sa.Column('standardized_name', sa.String(length=256), nullable=True))
        batch_op.create_index(batch_op.f('ix_compound_standardized_name'), ['standardized_name'], unique=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('compound', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_compound_standardized_name'))
        batch_op.drop_column('standardized_name')

    # ### end Alembic commands ###
