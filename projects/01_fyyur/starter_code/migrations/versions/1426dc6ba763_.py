"""empty message

Revision ID: 1426dc6ba763
Revises: a27bb3a932aa
Create Date: 2022-08-04 23:20:08.971270

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1426dc6ba763'
down_revision = 'a27bb3a932aa'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('shows', sa.Column('start_time', sa.DateTime(), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('shows', 'start_time')
    # ### end Alembic commands ###
