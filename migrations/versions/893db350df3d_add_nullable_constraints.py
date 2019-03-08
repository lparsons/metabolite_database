"""Add nullable constraints

Revision ID: 893db350df3d
Revises: 366f7e8e6b82
Create Date: 2019-03-07 16:58:31.382607

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '893db350df3d'
down_revision = '366f7e8e6b82'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('chromatography_method', schema=None) as batch_op:
        batch_op.alter_column('name',
               existing_type=sa.VARCHAR(length=128),
               nullable=False)

    with op.batch_alter_table('compound', schema=None) as batch_op:
        batch_op.alter_column('molecular_formula',
               existing_type=sa.VARCHAR(length=128),
               nullable=False)
        batch_op.alter_column('name',
               existing_type=sa.VARCHAR(length=256),
               nullable=False)

    with op.batch_alter_table('compound_list', schema=None) as batch_op:
        batch_op.alter_column('name',
               existing_type=sa.VARCHAR(length=256),
               nullable=False)

    with op.batch_alter_table('external_database', schema=None) as batch_op:
        batch_op.alter_column('name',
               existing_type=sa.VARCHAR(length=256),
               nullable=False)

    with op.batch_alter_table('retention_time', schema=None) as batch_op:
        batch_op.alter_column('compound_id',
               existing_type=sa.INTEGER(),
               nullable=False)

    with op.batch_alter_table('standard_run', schema=None) as batch_op:
        batch_op.alter_column('date',
               existing_type=sa.DATETIME(),
               nullable=False)
        batch_op.alter_column('operator',
               existing_type=sa.VARCHAR(length=256),
               nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('standard_run', schema=None) as batch_op:
        batch_op.alter_column('operator',
               existing_type=sa.VARCHAR(length=256),
               nullable=True)
        batch_op.alter_column('date',
               existing_type=sa.DATETIME(),
               nullable=True)

    with op.batch_alter_table('retention_time', schema=None) as batch_op:
        batch_op.alter_column('compound_id',
               existing_type=sa.INTEGER(),
               nullable=True)

    with op.batch_alter_table('external_database', schema=None) as batch_op:
        batch_op.alter_column('name',
               existing_type=sa.VARCHAR(length=256),
               nullable=True)

    with op.batch_alter_table('compound_list', schema=None) as batch_op:
        batch_op.alter_column('name',
               existing_type=sa.VARCHAR(length=256),
               nullable=True)

    with op.batch_alter_table('compound', schema=None) as batch_op:
        batch_op.alter_column('name',
               existing_type=sa.VARCHAR(length=256),
               nullable=True)
        batch_op.alter_column('molecular_formula',
               existing_type=sa.VARCHAR(length=128),
               nullable=True)

    with op.batch_alter_table('chromatography_method', schema=None) as batch_op:
        batch_op.alter_column('name',
               existing_type=sa.VARCHAR(length=128),
               nullable=True)

    # ### end Alembic commands ###