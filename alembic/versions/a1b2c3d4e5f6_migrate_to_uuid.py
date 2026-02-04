"""Migrate from Integer IDs to UUIDs

Revision ID: a1b2c3d4e5f6
Revises: 52b4512e07bf
Create Date: 2025-02-04 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = '52b4512e07bf'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade database schema from Integer IDs to UUIDs."""
    
    # Enable UUID extension if not already enabled
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
    
    # Step 1: Add new UUID columns to all tables
    op.add_column('users', sa.Column('id_new', UUID(as_uuid=True), nullable=True))
    op.add_column('customers', sa.Column('id_new', UUID(as_uuid=True), nullable=True))
    op.add_column('customers', sa.Column('user_id_new', UUID(as_uuid=True), nullable=True))
    op.add_column('businesses', sa.Column('id_new', UUID(as_uuid=True), nullable=True))
    op.add_column('businesses', sa.Column('user_id_new', UUID(as_uuid=True), nullable=True))
    op.add_column('otps', sa.Column('id_new', UUID(as_uuid=True), nullable=True))
    op.add_column('otps', sa.Column('user_id_new', UUID(as_uuid=True), nullable=True))
    op.add_column('refresh_tokens', sa.Column('id_new', UUID(as_uuid=True), nullable=True))
    op.add_column('refresh_tokens', sa.Column('user_id_new', UUID(as_uuid=True), nullable=True))
    
    # Step 2: Generate UUIDs for existing rows
    op.execute("UPDATE users SET id_new = uuid_generate_v4()")
    op.execute("UPDATE customers SET id_new = uuid_generate_v4()")
    op.execute("UPDATE businesses SET id_new = uuid_generate_v4()")
    op.execute("UPDATE otps SET id_new = uuid_generate_v4()")
    op.execute("UPDATE refresh_tokens SET id_new = uuid_generate_v4()")
    
    # Step 3: Update foreign keys to match new UUIDs
    op.execute("""
        UPDATE customers c
        SET user_id_new = u.id_new
        FROM users u
        WHERE c.user_id = u.id
    """)
    op.execute("""
        UPDATE businesses b
        SET user_id_new = u.id_new
        FROM users u
        WHERE b.user_id = u.id
    """)
    op.execute("""
        UPDATE otps o
        SET user_id_new = u.id_new
        FROM users u
        WHERE o.user_id = u.id
    """)
    op.execute("""
        UPDATE refresh_tokens rt
        SET user_id_new = u.id_new
        FROM users u
        WHERE rt.user_id = u.id
    """)
    
    # Step 4: Drop old foreign key constraints
    op.drop_constraint('customers_user_id_fkey', 'customers', type_='foreignkey')
    op.drop_constraint('businesses_user_id_fkey', 'businesses', type_='foreignkey')
    op.drop_constraint('otps_user_id_fkey', 'otps', type_='foreignkey')
    op.drop_constraint('refresh_tokens_user_id_fkey', 'refresh_tokens', type_='foreignkey')
    
    # Step 5: Drop old primary key constraints
    op.drop_constraint('users_pkey', 'users', type_='primary')
    op.drop_constraint('customers_pkey', 'customers', type_='primary')
    op.drop_constraint('businesses_pkey', 'businesses', type_='primary')
    op.drop_constraint('otps_pkey', 'otps', type_='primary')
    op.drop_constraint('refresh_tokens_pkey', 'refresh_tokens', type_='primary')
    
    # Step 6: Drop old indexes
    op.drop_index('ix_users_id', 'users')
    op.drop_index('ix_customers_id', 'customers')
    op.drop_index('ix_businesses_id', 'businesses')
    op.drop_index('ix_otps_id', 'otps')
    op.drop_index('ix_refresh_tokens_id', 'refresh_tokens')
    
    # Step 7: Drop old columns
    op.drop_column('users', 'id')
    op.drop_column('customers', 'id')
    op.drop_column('customers', 'user_id')
    op.drop_column('businesses', 'id')
    op.drop_column('businesses', 'user_id')
    op.drop_column('otps', 'id')
    op.drop_column('otps', 'user_id')
    op.drop_column('refresh_tokens', 'id')
    op.drop_column('refresh_tokens', 'user_id')
    
    # Step 8: Rename new columns to old names
    op.alter_column('users', 'id_new', new_column_name='id', nullable=False)
    op.alter_column('customers', 'id_new', new_column_name='id', nullable=False)
    op.alter_column('customers', 'user_id_new', new_column_name='user_id', nullable=False)
    op.alter_column('businesses', 'id_new', new_column_name='id', nullable=False)
    op.alter_column('businesses', 'user_id_new', new_column_name='user_id', nullable=False)
    op.alter_column('otps', 'id_new', new_column_name='id', nullable=False)
    op.alter_column('otps', 'user_id_new', new_column_name='user_id', nullable=False)
    op.alter_column('refresh_tokens', 'id_new', new_column_name='id', nullable=False)
    op.alter_column('refresh_tokens', 'user_id_new', new_column_name='user_id', nullable=False)
    
    # Step 9: Create new primary keys
    op.create_primary_key('users_pkey', 'users', ['id'])
    op.create_primary_key('customers_pkey', 'customers', ['id'])
    op.create_primary_key('businesses_pkey', 'businesses', ['id'])
    op.create_primary_key('otps_pkey', 'otps', ['id'])
    op.create_primary_key('refresh_tokens_pkey', 'refresh_tokens', ['id'])
    
    # Step 10: Create new foreign keys
    op.create_foreign_key('customers_user_id_fkey', 'customers', 'users', ['user_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('businesses_user_id_fkey', 'businesses', 'users', ['user_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('otps_user_id_fkey', 'otps', 'users', ['user_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('refresh_tokens_user_id_fkey', 'refresh_tokens', 'users', ['user_id'], ['id'], ondelete='CASCADE')
    
    # Step 11: Recreate indexes
    op.create_index('ix_users_id', 'users', ['id'])
    op.create_index('ix_customers_id', 'customers', ['id'])
    op.create_index('ix_businesses_id', 'businesses', ['id'])
    op.create_index('ix_otps_id', 'otps', ['id'])
    op.create_index('ix_refresh_tokens_id', 'refresh_tokens', ['id'])
    
    # Step 12: Update unique constraints for customers and businesses
    op.create_unique_constraint('customers_user_id_key', 'customers', ['user_id'])
    op.create_unique_constraint('businesses_user_id_key', 'businesses', ['user_id'])


def downgrade() -> None:
    """Downgrade database schema from UUIDs back to Integer IDs."""
    
    # Note: This downgrade will LOSE data relationships as we cannot
    # reliably convert UUIDs back to sequential integers while maintaining
    # foreign key relationships. This is provided for schema rollback only.
    
    # Step 1: Drop unique constraints
    op.drop_constraint('customers_user_id_key', 'customers', type_='unique')
    op.drop_constraint('businesses_user_id_key', 'businesses', type_='unique')
    
    # Step 2: Drop foreign key constraints
    op.drop_constraint('customers_user_id_fkey', 'customers', type_='foreignkey')
    op.drop_constraint('businesses_user_id_fkey', 'businesses', type_='foreignkey')
    op.drop_constraint('otps_user_id_fkey', 'otps', type_='foreignkey')
    op.drop_constraint('refresh_tokens_user_id_fkey', 'refresh_tokens', type_='foreignkey')
    
    # Step 3: Drop primary keys
    op.drop_constraint('users_pkey', 'users', type_='primary')
    op.drop_constraint('customers_pkey', 'customers', type_='primary')
    op.drop_constraint('businesses_pkey', 'businesses', type_='primary')
    op.drop_constraint('otps_pkey', 'otps', type_='primary')
    op.drop_constraint('refresh_tokens_pkey', 'refresh_tokens', type_='primary')
    
    # Step 4: Drop indexes
    op.drop_index('ix_users_id', 'users')
    op.drop_index('ix_customers_id', 'customers')
    op.drop_index('ix_businesses_id', 'businesses')
    op.drop_index('ix_otps_id', 'otps')
    op.drop_index('ix_refresh_tokens_id', 'refresh_tokens')
    
    # Step 5: Add new integer columns
    op.add_column('users', sa.Column('id_old', sa.Integer(), nullable=True))
    op.add_column('customers', sa.Column('id_old', sa.Integer(), nullable=True))
    op.add_column('customers', sa.Column('user_id_old', sa.Integer(), nullable=True))
    op.add_column('businesses', sa.Column('id_old', sa.Integer(), nullable=True))
    op.add_column('businesses', sa.Column('user_id_old', sa.Integer(), nullable=True))
    op.add_column('otps', sa.Column('id_old', sa.Integer(), nullable=True))
    op.add_column('otps', sa.Column('user_id_old', sa.Integer(), nullable=True))
    op.add_column('refresh_tokens', sa.Column('id_old', sa.Integer(), nullable=True))
    op.add_column('refresh_tokens', sa.Column('user_id_old', sa.Integer(), nullable=True))
    
    # Step 6: Generate sequential integers (data relationships will be lost)
    op.execute("UPDATE users SET id_old = row_number() OVER (ORDER BY created_at)")
    op.execute("UPDATE customers SET id_old = row_number() OVER (ORDER BY created_at)")
    op.execute("UPDATE businesses SET id_old = row_number() OVER (ORDER BY created_at)")
    op.execute("UPDATE otps SET id_old = row_number() OVER (ORDER BY created_at)")
    op.execute("UPDATE refresh_tokens SET id_old = row_number() OVER (ORDER BY created_at)")
    
    # Note: Foreign key relationships cannot be restored accurately
    # This downgrade is only for schema purposes
    
    # Step 7: Drop UUID columns
    op.drop_column('users', 'id')
    op.drop_column('customers', 'id')
    op.drop_column('customers', 'user_id')
    op.drop_column('businesses', 'id')
    op.drop_column('businesses', 'user_id')
    op.drop_column('otps', 'id')
    op.drop_column('otps', 'user_id')
    op.drop_column('refresh_tokens', 'id')
    op.drop_column('refresh_tokens', 'user_id')
    
    # Step 8: Rename integer columns back
    op.alter_column('users', 'id_old', new_column_name='id', nullable=False)
    op.alter_column('customers', 'id_old', new_column_name='id', nullable=False)
    op.alter_column('customers', 'user_id_old', new_column_name='user_id', nullable=False)
    op.alter_column('businesses', 'id_old', new_column_name='id', nullable=False)
    op.alter_column('businesses', 'user_id_old', new_column_name='user_id', nullable=False)
    op.alter_column('otps', 'id_old', new_column_name='id', nullable=False)
    op.alter_column('otps', 'user_id_old', new_column_name='user_id', nullable=False)
    op.alter_column('refresh_tokens', 'id_old', new_column_name='id', nullable=False)
    op.alter_column('refresh_tokens', 'user_id_old', new_column_name='user_id', nullable=False)
    
    # Step 9: Recreate primary keys
    op.create_primary_key('users_pkey', 'users', ['id'])
    op.create_primary_key('customers_pkey', 'customers', ['id'])
    op.create_primary_key('businesses_pkey', 'businesses', ['id'])
    op.create_primary_key('otps_pkey', 'otps', ['id'])
    op.create_primary_key('refresh_tokens_pkey', 'refresh_tokens', ['id'])
    
    # Step 10: Recreate indexes
    op.create_index('ix_users_id', 'users', ['id'])
    op.create_index('ix_customers_id', 'customers', ['id'])
    op.create_index('ix_businesses_id', 'businesses', ['id'])
    op.create_index('ix_otps_id', 'otps', ['id'])
    op.create_index('ix_refresh_tokens_id', 'refresh_tokens', ['id'])
