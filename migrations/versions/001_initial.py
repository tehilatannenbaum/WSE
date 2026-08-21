"""Initial migration

Revision ID: 001
Revises: 
Create Date: 2026-08-21 16:40:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create events table
    op.create_table(
        'events',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True, autoincrement=True),
        sa.Column('aggregate_id', sa.String(length=50), nullable=False),
        sa.Column('aggregate_type', sa.String(length=50), nullable=False),
        sa.Column('sequence_number', sa.Integer(), nullable=False),
        sa.Column('event_type', sa.String(length=50), nullable=False),
        sa.Column('payload', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.UniqueConstraint('aggregate_type', 'aggregate_id', 'sequence_number', name='uq_aggregate_seq')
    )
    op.create_index(op.f('ix_events_aggregate_id'), 'events', ['aggregate_id'], unique=False)
    op.create_index(op.f('ix_events_id'), 'events', ['id'], unique=False)

    # 2. Create users_read table
    op.create_table(
        'users_read',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True, autoincrement=True),
        sa.Column('username', sa.String(length=50), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('email', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True)
    )
    op.create_index(op.f('ix_users_read_id'), 'users_read', ['id'], unique=False)
    op.create_index(op.f('ix_users_read_username'), 'users_read', ['username'], unique=True)

    # 3. Create flights_read table
    op.create_table(
        'flights_read',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True, autoincrement=True),
        sa.Column('flight_number', sa.String(length=20), nullable=False),
        sa.Column('origin', sa.String(length=100), nullable=False),
        sa.Column('destination', sa.String(length=100), nullable=False),
        sa.Column('departure_time', sa.String(length=50), nullable=False),
        sa.Column('price', sa.Float(), nullable=False),
        sa.Column('available_seats', sa.Integer(), nullable=False),
        sa.Column('capacity', sa.Integer(), nullable=False),
        sa.Column('image_url', sa.String(length=500), nullable=True)
    )
    op.create_index(op.f('ix_flights_read_id'), 'flights_read', ['id'], unique=False)

    # 4. Create bookings_read table
    op.create_table(
        'bookings_read',
        sa.Column('id', sa.String(length=50), nullable=False, primary_key=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('flight_id', sa.Integer(), nullable=False),
        sa.Column('passenger_name', sa.String(length=100), nullable=False),
        sa.Column('passport_number', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True)
    )
    op.create_index(op.f('ix_bookings_read_id'), 'bookings_read', ['id'], unique=False)
    op.create_index(op.f('ix_bookings_read_user_id'), 'bookings_read', ['user_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_bookings_read_user_id'), table_name='bookings_read')
    op.drop_index(op.f('ix_bookings_read_id'), table_name='bookings_read')
    op.drop_table('bookings_read')
    
    op.drop_index(op.f('ix_flights_read_id'), table_name='flights_read')
    op.drop_table('flights_read')
    
    op.drop_index(op.f('ix_users_read_username'), table_name='users_read')
    op.drop_index(op.f('ix_users_read_id'), table_name='users_read')
    op.drop_table('users_read')
    
    op.drop_index(op.f('ix_events_id'), table_name='events')
    op.drop_index(op.f('ix_events_aggregate_id'), table_name='events')
    op.drop_table('events')
