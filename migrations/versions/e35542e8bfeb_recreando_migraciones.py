"""Recreando migraciones

Revision ID: e35542e8bfeb
Revises: 7e22e5231558
Create Date: 2025-02-20 11:25:43.268083

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'e35542e8bfeb'
down_revision = '7e22e5231558'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('requisitos_empresa', schema=None) as batch_op:
        batch_op.alter_column('tipo',
               existing_type=mysql.VARCHAR(length=255),
               nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('requisitos_empresa', schema=None) as batch_op:
        batch_op.alter_column('tipo',
               existing_type=mysql.VARCHAR(length=255),
               nullable=False)

    # ### end Alembic commands ###
