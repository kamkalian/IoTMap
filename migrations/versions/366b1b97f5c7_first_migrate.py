"""First migrate

Revision ID: 366b1b97f5c7
Revises: 
Create Date: 2020-03-22 12:07:38.262734

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '366b1b97f5c7'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('device',
    sa.Column('dev_id', sa.String(length=80), nullable=False),
    sa.Column('hardware_serial', sa.String(length=255), nullable=True),
    sa.PrimaryKeyConstraint('dev_id')
    )
    op.create_table('gateway',
    sa.Column('gtw_id', sa.String(length=80), nullable=False),
    sa.Column('gtw_trusted', sa.Boolean(), nullable=True),
    sa.Column('latitude', sa.Float(), nullable=True),
    sa.Column('longitude', sa.Float(), nullable=True),
    sa.Column('altitude', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('gtw_id')
    )
    op.create_table('message',
    sa.Column('msg_id', sa.Integer(), nullable=False),
    sa.Column('app_id', sa.String(length=255), nullable=True),
    sa.Column('port', sa.Integer(), nullable=True),
    sa.Column('counter', sa.Integer(), nullable=True),
    sa.Column('payload_raw', sa.String(length=1000), nullable=True),
    sa.Column('altitude', sa.Integer(), nullable=True),
    sa.Column('hdop', sa.Float(), nullable=True),
    sa.Column('latitude', sa.Float(), nullable=True),
    sa.Column('longitude', sa.Float(), nullable=True),
    sa.Column('sats', sa.Integer(), nullable=True),
    sa.Column('time', sa.DateTime(), nullable=True),
    sa.Column('frequency', sa.Float(), nullable=True),
    sa.Column('modulation', sa.String(length=64), nullable=True),
    sa.Column('data_rate', sa.String(length=64), nullable=True),
    sa.Column('airtime', sa.Integer(), nullable=True),
    sa.Column('coding_rate', sa.String(length=64), nullable=True),
    sa.Column('dev_id', sa.String(length=80), nullable=True),
    sa.ForeignKeyConstraint(['dev_id'], ['device.dev_id'], ),
    sa.PrimaryKeyConstraint('msg_id')
    )
    op.create_table('message_link',
    sa.Column('msg_link_id', sa.Integer(), nullable=False),
    sa.Column('timestamp', sa.Integer(), nullable=True),
    sa.Column('channel', sa.Integer(), nullable=True),
    sa.Column('rssi', sa.Integer(), nullable=True),
    sa.Column('snr', sa.Float(), nullable=True),
    sa.Column('rf_chain', sa.Integer(), nullable=True),
    sa.Column('msg_id', sa.Integer(), nullable=True),
    sa.Column('gtw_id', sa.String(length=80), nullable=True),
    sa.ForeignKeyConstraint(['gtw_id'], ['gateway.gtw_id'], ),
    sa.ForeignKeyConstraint(['msg_id'], ['message.msg_id'], ),
    sa.PrimaryKeyConstraint('msg_link_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('message_link')
    op.drop_table('message')
    op.drop_table('gateway')
    op.drop_table('device')
    # ### end Alembic commands ###
