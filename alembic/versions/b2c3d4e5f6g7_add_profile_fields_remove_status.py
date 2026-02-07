"""Add profile fields and remove status

Revision ID: b2c3d4e5f6g7
Revises: a1b2c3d4e5f6
Create Date: 2025-02-04 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ENUM

# revision identifiers, used by Alembic.
revision = 'b2c3d4e5f6g7'
down_revision = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add new profile fields, add ADMIN user type, and remove status field."""
    
    # Step 1: Add new columns to users table
    op.add_column('users', sa.Column('address', sa.String(255), nullable=True))
    op.add_column('users', sa.Column('city', sa.String(100), nullable=True))
    op.add_column('users', sa.Column('state', sa.String(100), nullable=True))
    op.add_column('users', sa.Column('country', sa.String(100), nullable=True))
    op.add_column('users', sa.Column('picture', sa.String(500), nullable=True))
    
    # Step 2: Create gender enum and add gender column
    gender_enum = ENUM('MALE', 'FEMALE', 'OTHER', 'PREFER_NOT_TO_SAY', name='gender', create_type=False)
    gender_enum.create(op.get_bind(), checkfirst=True)
    op.add_column('users', sa.Column('gender', gender_enum, nullable=True))
    
    # Step 3: Update UserType enum to include ADMIN
    # First, alter the existing enum to add ADMIN value
    op.execute("ALTER TYPE usertype ADD VALUE IF NOT EXISTS 'ADMIN'")
    
    # Step 4: Add have_subscription column to businesses table
    op.add_column('businesses', sa.Column('have_subscription', sa.Boolean(), nullable=False, server_default='false'))
    
    # Step 5: Remove status field and related constraints
    # Drop the index on status
    op.drop_index('idx_users_status', table_name='users')
    
    # Drop the status column
    op.drop_column('users', 'status')
    
    # Step 6: Drop the UserStatus enum type (it's no longer needed)
    op.execute("DROP TYPE IF EXISTS userstatus")


def downgrade() -> None:
    """Reverse the migration - restore status field and remove new profile fields."""
    
    # Step 1: Recreate UserStatus enum
    op.execute("CREATE TYPE userstatus AS ENUM ('PENDING', 'ACTIVE', 'SUSPENDED', 'DELETED')")
    
    # Step 2: Add status column back
    op.add_column('users', sa.Column('status', sa.String(50), nullable=False, server_default='PENDING'))
    
    # Step 3: Recreate status index
    op.create_index('idx_users_status', 'users', ['status'])
    
    # Step 4: Remove have_subscription from businesses
    op.drop_column('businesses', 'have_subscription')
    
    # Step 5: Remove ADMIN from UserType enum
    # Note: PostgreSQL doesn't support removing enum values directly
    # This would require recreating the enum type, which is complex
    # For downgrade purposes, we'll leave ADMIN in the enum
    
    # Step 6: Remove gender column and enum
    op.drop_column('users', 'gender')
    op.execute("DROP TYPE IF EXISTS gender")
    
    # Step 7: Remove new profile columns
    op.drop_column('users', 'picture')
    op.drop_column('users', 'country')
    op.drop_column('users', 'state')
    op.drop_column('users', 'city')
    op.drop_column('users', 'address')
