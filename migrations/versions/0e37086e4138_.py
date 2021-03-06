"""empty message

Revision ID: 0e37086e4138
Revises: 
Create Date: 2020-11-22 10:47:18.152024

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0e37086e4138'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('task_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'users', 'tasks', ['task_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'users', type_='foreignkey')
    op.drop_column('users', 'task_id')
    # ### end Alembic commands ###
