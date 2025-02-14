"""empty message

Revision ID: 88136831cc5c
Revises: d00ddcb0ba3e
Create Date: 2022-08-04 23:19:35.919425

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '88136831cc5c'
down_revision = 'd00ddcb0ba3e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Artist', sa.Column('website_link', sa.String(length=200), nullable=True))
    op.add_column('Artist', sa.Column('seeking_venue', sa.Boolean(), nullable=True))
    op.add_column('Artist', sa.Column('description', sa.String(length=300), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Artist', 'description')
    op.drop_column('Artist', 'seeking_venue')
    op.drop_column('Artist', 'website_link')
    # ### end Alembic commands ###
