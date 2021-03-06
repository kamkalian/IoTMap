"""Added model to gateway

Revision ID: 88f90fd2bd43
Revises: d9a79112f018
Create Date: 2020-03-25 19:58:00.667687

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '88f90fd2bd43'
down_revision = 'd9a79112f018'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('gateway', sa.Column('model', sa.String(length=64), nullable=True))
    op.create_index(op.f('ix_gateway_model'), 'gateway', ['model'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_gateway_model'), table_name='gateway')
    op.drop_column('gateway', 'model')
    # ### end Alembic commands ###
