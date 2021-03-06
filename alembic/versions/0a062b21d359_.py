"""empty message

Revision ID: 0a062b21d359
Revises: 
Create Date: 2021-11-21 18:05:03.569804

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0a062b21d359'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('accounts',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.Text(), nullable=True),
    sa.Column('username', sa.Text(), nullable=True),
    sa.Column('password', sa.Text(), nullable=True),
    sa.Column('email', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('username')
    )
    op.create_table('cookies',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('data', sa.Text(), nullable=True),
    sa.Column('account_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['account_id'], ['accounts.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('cookies')
    op.drop_table('accounts')
    # ### end Alembic commands ###
