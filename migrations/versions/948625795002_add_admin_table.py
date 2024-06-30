"""add Admin table

Revision ID: 948625795002
Revises: 15105ddb1a3a
Create Date: 2024-06-23 16:36:27.787694

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '948625795002'
down_revision = '15105ddb1a3a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('admins',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=30), nullable=False),
    sa.Column('password', sa.String(length=12), nullable=True),
    sa.Column('icon', sa.String(length=120), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('admins')
    # ### end Alembic commands ###
