"""empty message

Revision ID: d00ddcb0ba3e
Revises: 2afa06283a51
Create Date: 2022-08-04 23:19:15.409472

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd00ddcb0ba3e'
down_revision = '2afa06283a51'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Venue', sa.Column('upcoming_show', sa.Integer(), nullable=True))
    op.add_column('Venue', sa.Column('website_link', sa.String(length=200), nullable=True))
    op.add_column('Venue', sa.Column('seeking_talent', sa.Boolean(), nullable=True))
    op.add_column('Venue', sa.Column('description', sa.String(length=300), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Venue', 'description')
    op.drop_column('Venue', 'seeking_talent')
    op.drop_column('Venue', 'website_link')
    op.drop_column('Venue', 'upcoming_show')
    # ### end Alembic commands ###
