"""Add v2.0 game features

Revision ID: 0001
Revises: 
Create Date: 2025-01-13 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create artifacts table
    op.create_table('artifacts',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('artifact_type', sa.String(), nullable=False),
    sa.Column('rarity', sa.String(), nullable=False),
    sa.Column('bonus_percentage', sa.Float(), nullable=False),
    sa.Column('is_equipped', sa.Boolean(), nullable=True, default=False),
    sa.Column('discovered_at', sa.DateTime(), nullable=True),
    sa.Column('equipped_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_artifacts_id'), 'artifacts', ['id'], unique=False)

    # Create ascension_tiers table
    op.create_table('ascension_tiers',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('current_tier', sa.Integer(), nullable=True, default=0),
    sa.Column('ascension_count', sa.Integer(), nullable=True, default=0),
    sa.Column('total_stardust_earned', sa.Float(), nullable=True, default=0.0),
    sa.Column('last_ascension_at', sa.DateTime(), nullable=True),
    sa.Column('stellar_shards_sacrificed', sa.Float(), nullable=True, default=0.0),
    sa.Column('lumina_sacrificed', sa.Float(), nullable=True, default=0.0),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ascension_tiers_id'), 'ascension_tiers', ['id'], unique=False)

    # Create lottery_rounds table
    op.create_table('lottery_rounds',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('round_number', sa.Integer(), nullable=False),
    sa.Column('start_date', sa.DateTime(), nullable=False),
    sa.Column('end_date', sa.DateTime(), nullable=False),
    sa.Column('total_pool', sa.Float(), nullable=True, default=0.0),
    sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
    sa.Column('is_completed', sa.Boolean(), nullable=True, default=False),
    sa.Column('grand_prize_winner_id', sa.Integer(), nullable=True),
    sa.Column('second_prize_winner_id', sa.Integer(), nullable=True),
    sa.Column('third_prize_winner_id', sa.Integer(), nullable=True),
    sa.Column('grand_prize_amount', sa.Float(), nullable=True, default=0.0),
    sa.Column('second_prize_amount', sa.Float(), nullable=True, default=0.0),
    sa.Column('third_prize_amount', sa.Float(), nullable=True, default=0.0),
    sa.Column('consolation_prize_amount', sa.Float(), nullable=True, default=0.0),
    sa.ForeignKeyConstraint(['grand_prize_winner_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['second_prize_winner_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['third_prize_winner_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('round_number')
    )
    op.create_index(op.f('ix_lottery_rounds_id'), 'lottery_rounds', ['id'], unique=False)

    # Create shield_dust table
    op.create_table('shield_dust',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('total_shield_dust', sa.Float(), nullable=True, default=0.0),
    sa.Column('shield_dust_used', sa.Float(), nullable=True, default=0.0),
    sa.Column('total_protection_provided', sa.Float(), nullable=True, default=0.0),
    sa.Column('real_trades_completed', sa.Integer(), nullable=True, default=0),
    sa.Column('losses_mitigated', sa.Float(), nullable=True, default=0.0),
    sa.Column('protection_events', sa.Integer(), nullable=True, default=0),
    sa.Column('current_shield_type', sa.String(), nullable=True, default='none'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_shield_dust_id'), 'shield_dust', ['id'], unique=False)

    # Create quantum_anomalies table
    op.create_table('quantum_anomalies',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('anomaly_type', sa.String(), nullable=False),
    sa.Column('rarity', sa.String(), nullable=False),
    sa.Column('description', sa.Text(), nullable=False),
    sa.Column('effect_description', sa.Text(), nullable=False),
    sa.Column('trigger_chance', sa.Float(), nullable=False),
    sa.Column('required_volume', sa.Float(), nullable=True, default=0.0),
    sa.Column('duration_hours', sa.Integer(), nullable=True, default=24),
    sa.Column('artifact_drop_chance', sa.Float(), nullable=True, default=0.0),
    sa.Column('stellar_shard_bonus', sa.Float(), nullable=True, default=0.0),
    sa.Column('xp_multiplier', sa.Float(), nullable=True, default=1.0),
    sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_quantum_anomalies_id'), 'quantum_anomalies', ['id'], unique=False)

    # Create cosmic_genesis_tiles table
    op.create_table('cosmic_genesis_tiles',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('tile_id', sa.String(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('description', sa.Text(), nullable=False),
    sa.Column('tile_type', sa.String(), nullable=False),
    sa.Column('category', sa.String(), nullable=False),
    sa.Column('grid_x', sa.Integer(), nullable=False),
    sa.Column('grid_y', sa.Integer(), nullable=False),
    sa.Column('base_cost', sa.Float(), nullable=False),
    sa.Column('cost_scaling', sa.Float(), nullable=True, default=1.1),
    sa.Column('effect_description', sa.Text(), nullable=False),
    sa.Column('effect_data', sa.JSON(), nullable=True),
    sa.Column('prerequisite_tiles', sa.JSON(), nullable=True),
    sa.Column('min_level', sa.Integer(), nullable=True, default=1),
    sa.Column('min_ascension_tier', sa.Integer(), nullable=True, default=0),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('tile_id')
    )
    op.create_index(op.f('ix_cosmic_genesis_tiles_id'), 'cosmic_genesis_tiles', ['id'], unique=False)

    # Create lottery_tickets table
    op.create_table('lottery_tickets',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('lottery_round_id', sa.Integer(), nullable=False),
    sa.Column('ticket_number', sa.String(), nullable=False),
    sa.Column('purchase_date', sa.DateTime(), nullable=True),
    sa.Column('cost_stellar_shards', sa.Float(), nullable=True, default=100.0),
    sa.Column('is_winner', sa.Boolean(), nullable=True, default=False),
    sa.Column('prize_tier', sa.String(), nullable=True),
    sa.Column('prize_amount', sa.Float(), nullable=True, default=0.0),
    sa.ForeignKeyConstraint(['lottery_round_id'], ['lottery_rounds.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_lottery_tickets_id'), 'lottery_tickets', ['id'], unique=False)

    # Create quantum_anomaly_events table
    op.create_table('quantum_anomaly_events',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('anomaly_id', sa.Integer(), nullable=False),
    sa.Column('start_time', sa.DateTime(), nullable=False),
    sa.Column('end_time', sa.DateTime(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
    sa.Column('is_completed', sa.Boolean(), nullable=True, default=False),
    sa.Column('total_participants', sa.Integer(), nullable=True, default=0),
    sa.Column('completion_threshold', sa.Float(), nullable=True, default=100.0),
    sa.Column('current_progress', sa.Float(), nullable=True, default=0.0),
    sa.ForeignKeyConstraint(['anomaly_id'], ['quantum_anomalies.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_quantum_anomaly_events_id'), 'quantum_anomaly_events', ['id'], unique=False)

    # Create user_cosmic_progress table
    op.create_table('user_cosmic_progress',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('tile_id', sa.String(), nullable=False),
    sa.Column('unlock_level', sa.Integer(), nullable=True, default=0),
    sa.Column('total_invested', sa.Float(), nullable=True, default=0.0),
    sa.Column('unlocked_at', sa.DateTime(), nullable=True),
    sa.Column('last_upgraded_at', sa.DateTime(), nullable=True),
    sa.Column('current_effect_multiplier', sa.Float(), nullable=True, default=1.0),
    sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
    sa.ForeignKeyConstraint(['tile_id'], ['cosmic_genesis_tiles.tile_id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_cosmic_progress_id'), 'user_cosmic_progress', ['id'], unique=False)

    # Create user_game_stats table
    op.create_table('user_game_stats',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('stellar_shards', sa.Float(), nullable=True, default=0.0),
    sa.Column('lumina', sa.Float(), nullable=True, default=0.0),
    sa.Column('stardust', sa.Float(), nullable=True, default=0.0),
    sa.Column('total_trades', sa.Integer(), nullable=True, default=0),
    sa.Column('successful_trades', sa.Integer(), nullable=True, default=0),
    sa.Column('total_profit_loss', sa.Float(), nullable=True, default=0.0),
    sa.Column('best_trade_profit', sa.Float(), nullable=True, default=0.0),
    sa.Column('worst_trade_loss', sa.Float(), nullable=True, default=0.0),
    sa.Column('current_streak', sa.Integer(), nullable=True, default=0),
    sa.Column('best_streak', sa.Integer(), nullable=True, default=0),
    sa.Column('last_trade_date', sa.DateTime(), nullable=True),
    sa.Column('cosmic_tier', sa.Integer(), nullable=True, default=0),
    sa.Column('total_artifacts_discovered', sa.Integer(), nullable=True, default=0),
    sa.Column('total_anomalies_participated', sa.Integer(), nullable=True, default=0),
    sa.Column('total_lottery_tickets_bought', sa.Integer(), nullable=True, default=0),
    sa.Column('total_xp_multiplier', sa.Float(), nullable=True, default=1.0),
    sa.Column('total_earning_multiplier', sa.Float(), nullable=True, default=1.0),
    sa.Column('total_luck_multiplier', sa.Float(), nullable=True, default=1.0),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_game_stats_id'), 'user_game_stats', ['id'], unique=False)

    # Create anomaly_participations table
    op.create_table('anomaly_participations',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('event_id', sa.Integer(), nullable=False),
    sa.Column('participation_score', sa.Float(), nullable=True, default=0.0),
    sa.Column('rewards_earned', sa.JSON(), nullable=True),
    sa.Column('participated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['event_id'], ['quantum_anomaly_events.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_anomaly_participations_id'), 'anomaly_participations', ['id'], unique=False)

    # Create shield_protection_events table
    op.create_table('shield_protection_events',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('shield_dust_id', sa.Integer(), nullable=False),
    sa.Column('trade_id', sa.Integer(), nullable=False),
    sa.Column('loss_amount', sa.Float(), nullable=False),
    sa.Column('protection_amount', sa.Float(), nullable=False),
    sa.Column('shield_dust_consumed', sa.Float(), nullable=False),
    sa.Column('protected_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['shield_dust_id'], ['shield_dust.id'], ),
    sa.ForeignKeyConstraint(['trade_id'], ['trades.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_shield_protection_events_id'), 'shield_protection_events', ['id'], unique=False)

    # Add new columns to existing trades table
    op.add_column('trades', sa.Column('is_real_trade', sa.Boolean(), nullable=True, default=False))
    op.add_column('trades', sa.Column('stellar_shards_earned', sa.Float(), nullable=True, default=0.0))
    op.add_column('trades', sa.Column('lumina_earned', sa.Float(), nullable=True, default=0.0))


def downgrade() -> None:
    # Remove added columns from trades table
    op.drop_column('trades', 'lumina_earned')
    op.drop_column('trades', 'stellar_shards_earned')
    op.drop_column('trades', 'is_real_trade')
    
    # Drop all new tables in reverse order
    op.drop_index(op.f('ix_shield_protection_events_id'), table_name='shield_protection_events')
    op.drop_table('shield_protection_events')
    op.drop_index(op.f('ix_anomaly_participations_id'), table_name='anomaly_participations')
    op.drop_table('anomaly_participations')
    op.drop_index(op.f('ix_user_game_stats_id'), table_name='user_game_stats')
    op.drop_table('user_game_stats')
    op.drop_index(op.f('ix_user_cosmic_progress_id'), table_name='user_cosmic_progress')
    op.drop_table('user_cosmic_progress')
    op.drop_index(op.f('ix_quantum_anomaly_events_id'), table_name='quantum_anomaly_events')
    op.drop_table('quantum_anomaly_events')
    op.drop_index(op.f('ix_lottery_tickets_id'), table_name='lottery_tickets')
    op.drop_table('lottery_tickets')
    op.drop_index(op.f('ix_cosmic_genesis_tiles_id'), table_name='cosmic_genesis_tiles')
    op.drop_table('cosmic_genesis_tiles')
    op.drop_index(op.f('ix_quantum_anomalies_id'), table_name='quantum_anomalies')
    op.drop_table('quantum_anomalies')
    op.drop_index(op.f('ix_shield_dust_id'), table_name='shield_dust')
    op.drop_table('shield_dust')
    op.drop_index(op.f('ix_lottery_rounds_id'), table_name='lottery_rounds')
    op.drop_table('lottery_rounds')
    op.drop_index(op.f('ix_ascension_tiers_id'), table_name='ascension_tiers')
    op.drop_table('ascension_tiers')
    op.drop_index(op.f('ix_artifacts_id'), table_name='artifacts')
    op.drop_table('artifacts')