"""Replace JWT with simple tokens

Revision ID: c3d4e5f6g7h8
Revises: b2c3d4e5f6g7
Create Date: 2026-02-04 02:45:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision = 'c3d4e5f6g7h8'
down_revision = 'b2c3d4e5f6g7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create access_tokens table and drop refresh_tokens table."""
    
    # Step 1: Create new access_tokens table
    op.create_table(
        'access_tokens',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('token_hash', sa.String(64), nullable=False, unique=True),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('user_agent', sa.String(512), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
    )
    
    # Step 2: Create indexes for performance
    op.create_index('idx_access_tokens_token_hash', 'access_tokens', ['token_hash'], unique=True)
    op.create_index('idx_access_tokens_user_id', 'access_tokens', ['user_id'])
    op.create_index('idx_access_tokens_expires_at', 'access_tokens', ['expires_at'])
    
    # Step 3: Drop old refresh_tokens table (if exists)
    op.execute("DROP TABLE IF EXISTS refresh_tokens CASCADE")


def downgrade() -> None:
    """Revert to JWT with refresh_tokens table."""
    
    # Step 1: Recreate refresh_tokens table
    op.create_table(
        'refresh_tokens',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('token', sa.String(512), nullable=False, unique=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_revoked', sa.Boolean(), default=False, nullable=False),
        sa.Column('revoked_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
    )
    
    # Step 2: Recreate refresh_tokens indexes
    op.create_index('idx_refresh_tokens_user_id', 'refresh_tokens', ['user_id'])
    op.create_index('idx_refresh_tokens_expires_at', 'refresh_tokens', ['expires_at'])
    op.create_index('idx_refresh_tokens_token', 'refresh_tokens', ['token'], unique=True)
    op.create_index('idx_refresh_tokens_is_revoked', 'refresh_tokens', ['is_revoked'])
    
    # Step 3: Drop access_tokens table
    op.drop_index('idx_access_tokens_expires_at', table_name='access_tokens')
    op.drop_index('idx_access_tokens_user_id', table_name='access_tokens')
    op.drop_index('idx_access_tokens_token_hash', table_name='access_tokens')
    op.drop_table('access_tokens')
