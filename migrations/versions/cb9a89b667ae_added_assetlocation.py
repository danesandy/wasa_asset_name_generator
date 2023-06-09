"""Added AssetLocation

Revision ID: cb9a89b667ae
Revises: bee1e8ac6d74
Create Date: 2023-06-23 15:50:38.263835

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cb9a89b667ae'
down_revision = 'bee1e8ac6d74'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('asset_location',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('location_code_id', sa.Integer(), nullable=False),
    sa.Column('process_code_id', sa.Integer(), nullable=False),
    sa.Column('asset_type_id', sa.Integer(), nullable=False),
    sa.Column('local_number', sa.Integer(), nullable=False),
    sa.Column('duplicate_status', sa.String(length=1), nullable=True),
    sa.ForeignKeyConstraint(['asset_type_id'], ['asset_type.id'], ),
    sa.ForeignKeyConstraint(['location_code_id'], ['location_code.id'], ),
    sa.ForeignKeyConstraint(['process_code_id'], ['process_code.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('asset', schema=None) as batch_op:
        batch_op.add_column(sa.Column('asset_location_id', sa.Integer(), nullable=True))
        batch_op.drop_constraint('asset_asset_type_id_fkey', type_='foreignkey')
        batch_op.drop_constraint('asset_process_code_id_fkey', type_='foreignkey')
        batch_op.drop_constraint('asset_location_code_id_fkey', type_='foreignkey')
        batch_op.create_foreign_key(None, 'asset_location', ['asset_location_id'], ['id'])
        batch_op.drop_column('duplicate_status')
        batch_op.drop_column('asset_type_id')
        batch_op.drop_column('location_code_id')
        batch_op.drop_column('local_number')
        batch_op.drop_column('process_code_id')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('asset', schema=None) as batch_op:
        batch_op.add_column(sa.Column('process_code_id', sa.INTEGER(), autoincrement=False, nullable=False))
        batch_op.add_column(sa.Column('local_number', sa.INTEGER(), autoincrement=False, nullable=False))
        batch_op.add_column(sa.Column('location_code_id', sa.INTEGER(), autoincrement=False, nullable=False))
        batch_op.add_column(sa.Column('asset_type_id', sa.INTEGER(), autoincrement=False, nullable=False))
        batch_op.add_column(sa.Column('duplicate_status', sa.VARCHAR(length=1), autoincrement=False, nullable=True))
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key('asset_location_code_id_fkey', 'location_code', ['location_code_id'], ['id'])
        batch_op.create_foreign_key('asset_process_code_id_fkey', 'process_code', ['process_code_id'], ['id'])
        batch_op.create_foreign_key('asset_asset_type_id_fkey', 'asset_type', ['asset_type_id'], ['id'])
        batch_op.drop_column('asset_location_id')

    op.drop_table('asset_location')
    # ### end Alembic commands ###
