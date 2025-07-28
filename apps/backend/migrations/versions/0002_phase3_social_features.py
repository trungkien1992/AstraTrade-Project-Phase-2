"""Phase 3 Social Features

Revision ID: 0002_phase3_social_features
Revises: 0001_initial_game_features
Create Date: 2024-01-16 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '0002_phase3_social_features'
down_revision = '0001_initial_game_features'
branch_labels = None
depends_on = None


def upgrade():
    # Create constellations table
    op.create_table(
        'constellations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('owner_id', sa.Integer(), nullable=False),
        sa.Column('member_count', sa.Integer(), default=0),
        sa.Column('total_stellar_shards', sa.Float(), default=0.0),
        sa.Column('total_lumina', sa.Float(), default=0.0),
        sa.Column('constellation_level', sa.Integer(), default=1),
        sa.Column('constellation_color', sa.String(7), default='#7B2CBF'),
        sa.Column('constellation_emblem', sa.String(50), default='star'),
        sa.Column('is_public', sa.Boolean(), default=True),
        sa.Column('max_members', sa.Integer(), default=50),
        sa.Column('total_battles', sa.Integer(), default=0),
        sa.Column('battles_won', sa.Integer(), default=0),
        sa.Column('battle_rating', sa.Float(), default=1000.0),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), default=sa.func.now(), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id']),
        sa.UniqueConstraint('name')
    )

    # Create constellation_memberships table
    op.create_table(
        'constellation_memberships',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('constellation_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('role', sa.String(20), default='member'),
        sa.Column('contribution_score', sa.Integer(), default=0),
        sa.Column('stellar_shards_contributed', sa.Float(), default=0.0),
        sa.Column('lumina_contributed', sa.Float(), default=0.0),
        sa.Column('battles_participated', sa.Integer(), default=0),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('joined_at', sa.DateTime(), default=sa.func.now()),
        sa.Column('last_active_at', sa.DateTime(), default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['constellation_id'], ['constellations.id']),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.UniqueConstraint('constellation_id', 'user_id', name='unique_constellation_membership')
    )

    # Create constellation_battles table
    op.create_table(
        'constellation_battles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('challenger_constellation_id', sa.Integer(), nullable=False),
        sa.Column('defender_constellation_id', sa.Integer(), nullable=False),
        sa.Column('battle_type', sa.String(50), nullable=False),
        sa.Column('duration_hours', sa.Integer(), default=24),
        sa.Column('status', sa.String(20), default='pending'),
        sa.Column('winner_constellation_id', sa.Integer(), nullable=True),
        sa.Column('challenger_score', sa.Float(), default=0.0),
        sa.Column('defender_score', sa.Float(), default=0.0),
        sa.Column('total_participants', sa.Integer(), default=0),
        sa.Column('prize_pool', sa.Float(), default=0.0),
        sa.Column('winner_reward', sa.Float(), default=0.0),
        sa.Column('rewards_distributed', sa.Boolean(), default=False),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['challenger_constellation_id'], ['constellations.id']),
        sa.ForeignKeyConstraint(['defender_constellation_id'], ['constellations.id']),
        sa.ForeignKeyConstraint(['winner_constellation_id'], ['constellations.id'])
    )

    # Create constellation_battle_participations table
    op.create_table(
        'constellation_battle_participations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('battle_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('constellation_id', sa.Integer(), nullable=False),
        sa.Column('individual_score', sa.Float(), default=0.0),
        sa.Column('trades_completed', sa.Integer(), default=0),
        sa.Column('stellar_shards_earned', sa.Float(), default=0.0),
        sa.Column('contribution_percentage', sa.Float(), default=0.0),
        sa.Column('individual_reward', sa.Float(), default=0.0),
        sa.Column('bonus_xp', sa.Integer(), default=0),
        sa.Column('joined_at', sa.DateTime(), default=sa.func.now()),
        sa.Column('last_activity_at', sa.DateTime(), default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['battle_id'], ['constellation_battles.id']),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.ForeignKeyConstraint(['constellation_id'], ['constellations.id'])
    )

    # Create user_prestige table
    op.create_table(
        'user_prestige',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('is_verified', sa.Boolean(), default=False),
        sa.Column('verification_tier', sa.Integer(), default=0),
        sa.Column('verification_date', sa.DateTime(), nullable=True),
        sa.Column('spotlight_eligible', sa.Boolean(), default=False),
        sa.Column('aura_color', sa.String(7), default='#FFFFFF'),
        sa.Column('custom_title', sa.String(100), nullable=True),
        sa.Column('badge_collection', sa.JSON(), default=list),
        sa.Column('spotlight_count', sa.Integer(), default=0),
        sa.Column('last_spotlight_date', sa.DateTime(), nullable=True),
        sa.Column('spotlight_votes', sa.Integer(), default=0),
        sa.Column('social_rating', sa.Float(), default=0.0),
        sa.Column('influence_score', sa.Float(), default=0.0),
        sa.Column('community_contributions', sa.Integer(), default=0),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), default=sa.func.now(), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.UniqueConstraint('user_id')
    )

    # Create viral_content table
    op.create_table(
        'viral_content',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('content_type', sa.String(50), nullable=False),
        sa.Column('content_title', sa.String(200), nullable=False),
        sa.Column('content_description', sa.Text(), nullable=True),
        sa.Column('content_data', sa.JSON(), nullable=False),
        sa.Column('share_count', sa.Integer(), default=0),
        sa.Column('viral_score', sa.Integer(), default=0),
        sa.Column('engagement_rate', sa.Float(), default=0.0),
        sa.Column('platform_shares', sa.JSON(), default=dict),
        sa.Column('template_id', sa.String(50), nullable=True),
        sa.Column('trading_context', sa.JSON(), nullable=True),
        sa.Column('achievement_context', sa.JSON(), nullable=True),
        sa.Column('is_public', sa.Boolean(), default=True),
        sa.Column('is_featured', sa.Boolean(), default=False),
        sa.Column('moderation_status', sa.String(20), default='approved'),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
        sa.Column('last_shared_at', sa.DateTime(), default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'])
    )

    # Create fomo_events table
    op.create_table(
        'fomo_events',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('event_name', sa.String(100), nullable=False),
        sa.Column('event_type', sa.String(50), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('max_participants', sa.Integer(), nullable=True),
        sa.Column('participation_requirements', sa.JSON(), default=dict),
        sa.Column('reward_type', sa.String(50), nullable=False),
        sa.Column('reward_data', sa.JSON(), nullable=False),
        sa.Column('start_time', sa.DateTime(), nullable=False),
        sa.Column('end_time', sa.DateTime(), nullable=False),
        sa.Column('urgency_level', sa.Integer(), default=1),
        sa.Column('current_participants', sa.Integer(), default=0),
        sa.Column('completion_threshold', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('is_completed', sa.Boolean(), default=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Create fomo_event_participations table
    op.create_table(
        'fomo_event_participations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('event_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('participation_score', sa.Float(), default=0.0),
        sa.Column('requirements_met', sa.JSON(), default=dict),
        sa.Column('reward_earned', sa.Boolean(), default=False),
        sa.Column('reward_claimed', sa.Boolean(), default=False),
        sa.Column('reward_data', sa.JSON(), nullable=True),
        sa.Column('joined_at', sa.DateTime(), default=sa.func.now()),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['event_id'], ['fomo_events.id']),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'])
    )

    # Create indexes for better performance
    op.create_index('idx_constellations_public', 'constellations', ['is_public'])
    op.create_index('idx_constellations_level', 'constellations', ['constellation_level'])
    op.create_index('idx_constellations_rating', 'constellations', ['battle_rating'])
    
    op.create_index('idx_constellation_memberships_active', 'constellation_memberships', ['is_active'])
    op.create_index('idx_constellation_memberships_role', 'constellation_memberships', ['role'])
    
    op.create_index('idx_constellation_battles_status', 'constellation_battles', ['status'])
    op.create_index('idx_constellation_battles_type', 'constellation_battles', ['battle_type'])
    
    op.create_index('idx_user_prestige_verified', 'user_prestige', ['is_verified'])
    op.create_index('idx_user_prestige_spotlight', 'user_prestige', ['spotlight_eligible'])
    
    op.create_index('idx_viral_content_type', 'viral_content', ['content_type'])
    op.create_index('idx_viral_content_public', 'viral_content', ['is_public'])
    op.create_index('idx_viral_content_viral_score', 'viral_content', ['viral_score'])
    
    op.create_index('idx_fomo_events_active', 'fomo_events', ['is_active'])
    op.create_index('idx_fomo_events_time', 'fomo_events', ['start_time', 'end_time'])


def downgrade():
    # Drop indexes
    op.drop_index('idx_fomo_events_time')
    op.drop_index('idx_fomo_events_active')
    op.drop_index('idx_viral_content_viral_score')
    op.drop_index('idx_viral_content_public')
    op.drop_index('idx_viral_content_type')
    op.drop_index('idx_user_prestige_spotlight')
    op.drop_index('idx_user_prestige_verified')
    op.drop_index('idx_constellation_battles_type')
    op.drop_index('idx_constellation_battles_status')
    op.drop_index('idx_constellation_memberships_role')
    op.drop_index('idx_constellation_memberships_active')
    op.drop_index('idx_constellations_rating')
    op.drop_index('idx_constellations_level')
    op.drop_index('idx_constellations_public')

    # Drop tables in reverse order
    op.drop_table('fomo_event_participations')
    op.drop_table('fomo_events')
    op.drop_table('viral_content')
    op.drop_table('user_prestige')
    op.drop_table('constellation_battle_participations')
    op.drop_table('constellation_battles')
    op.drop_table('constellation_memberships')
    op.drop_table('constellations')