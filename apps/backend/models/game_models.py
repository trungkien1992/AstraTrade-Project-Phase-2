from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
try:
    from ..core.database import Base
except ImportError:
    from core.database import Base


# NFT Artifact System Models
class Artifact(Base):
    __tablename__ = "artifacts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    artifact_type = Column(String, nullable=False)  # forger_efficiency, upgrade_discount, etc.
    rarity = Column(String, nullable=False)  # common, rare, epic, legendary
    bonus_percentage = Column(Float, nullable=False)
    is_equipped = Column(Boolean, default=False)
    discovered_at = Column(DateTime, default=datetime.utcnow)
    equipped_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="artifacts")


# Cosmic Ascension System Models
class AscensionTier(Base):
    __tablename__ = "ascension_tiers"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    current_tier = Column(Integer, default=0)  # 0-5 (Voyager to Infinity Guard)
    ascension_count = Column(Integer, default=0)
    total_stardust_earned = Column(Float, default=0.0)
    last_ascension_at = Column(DateTime, nullable=True)
    
    # Progression tracking
    stellar_shards_sacrificed = Column(Float, default=0.0)
    lumina_sacrificed = Column(Float, default=0.0)
    
    # Relationships
    user = relationship("User", back_populates="ascension_tier")


# Stardust Lottery System Models
class LotteryRound(Base):
    __tablename__ = "lottery_rounds"
    
    id = Column(Integer, primary_key=True, index=True)
    round_number = Column(Integer, unique=True, nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    total_pool = Column(Float, default=0.0)
    is_active = Column(Boolean, default=True)
    is_completed = Column(Boolean, default=False)
    
    # Winner tracking
    grand_prize_winner_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    second_prize_winner_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    third_prize_winner_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Prize amounts
    grand_prize_amount = Column(Float, default=0.0)
    second_prize_amount = Column(Float, default=0.0)
    third_prize_amount = Column(Float, default=0.0)
    consolation_prize_amount = Column(Float, default=0.0)
    
    # Relationships
    tickets = relationship("LotteryTicket", back_populates="lottery_round")


class LotteryTicket(Base):
    __tablename__ = "lottery_tickets"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    lottery_round_id = Column(Integer, ForeignKey("lottery_rounds.id"), nullable=False)
    ticket_number = Column(String, nullable=False)
    purchase_date = Column(DateTime, default=datetime.utcnow)
    cost_stellar_shards = Column(Float, default=100.0)
    is_winner = Column(Boolean, default=False)
    prize_tier = Column(String, nullable=True)  # grand, second, third, consolation
    prize_amount = Column(Float, default=0.0)
    
    # Relationships
    user = relationship("User", back_populates="lottery_tickets")
    lottery_round = relationship("LotteryRound", back_populates="tickets")


# Shield Dust Protection System Models
class ShieldDust(Base):
    __tablename__ = "shield_dust"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    total_shield_dust = Column(Float, default=0.0)
    shield_dust_used = Column(Float, default=0.0)
    total_protection_provided = Column(Float, default=0.0)
    real_trades_completed = Column(Integer, default=0)
    
    # Shield effectiveness tracking
    losses_mitigated = Column(Float, default=0.0)
    protection_events = Column(Integer, default=0)
    
    # Visual shield type based on amount
    current_shield_type = Column(String, default="none")  # none, basic, enhanced, legendary, cosmic
    
    # Relationships
    user = relationship("User", back_populates="shield_dust")
    protection_events_rel = relationship("ShieldProtectionEvent", back_populates="shield_dust")


class ShieldProtectionEvent(Base):
    __tablename__ = "shield_protection_events"
    
    id = Column(Integer, primary_key=True, index=True)
    shield_dust_id = Column(Integer, ForeignKey("shield_dust.id"), nullable=False)
    trade_id = Column(Integer, ForeignKey("trades.id"), nullable=False)
    loss_amount = Column(Float, nullable=False)
    protection_amount = Column(Float, nullable=False)
    shield_dust_consumed = Column(Float, nullable=False)
    protected_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    shield_dust = relationship("ShieldDust", back_populates="protection_events_rel")
    trade = relationship("Trade", back_populates="shield_protection")


# Quantum Anomaly System Models
class QuantumAnomaly(Base):
    __tablename__ = "quantum_anomalies"
    
    id = Column(Integer, primary_key=True, index=True)
    anomaly_type = Column(String, nullable=False)  # temporal_flux, reality_convergence, etc.
    rarity = Column(String, nullable=False)  # common, rare, epic, legendary
    description = Column(Text, nullable=False)
    effect_description = Column(Text, nullable=False)
    
    # Trigger conditions
    trigger_chance = Column(Float, nullable=False)  # Daily percentage chance
    required_volume = Column(Float, default=0.0)
    duration_hours = Column(Integer, default=24)
    
    # Rewards
    artifact_drop_chance = Column(Float, default=0.0)
    stellar_shard_bonus = Column(Float, default=0.0)
    xp_multiplier = Column(Float, default=1.0)
    
    # Status
    is_active = Column(Boolean, default=True)


class QuantumAnomalyEvent(Base):
    __tablename__ = "quantum_anomaly_events"
    
    id = Column(Integer, primary_key=True, index=True)
    anomaly_id = Column(Integer, ForeignKey("quantum_anomalies.id"), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)
    is_completed = Column(Boolean, default=False)
    
    # Participation tracking
    total_participants = Column(Integer, default=0)
    completion_threshold = Column(Float, default=100.0)
    current_progress = Column(Float, default=0.0)
    
    # Relationships
    anomaly = relationship("QuantumAnomaly")
    participations = relationship("AnomalyParticipation", back_populates="event")


class AnomalyParticipation(Base):
    __tablename__ = "anomaly_participations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    event_id = Column(Integer, ForeignKey("quantum_anomaly_events.id"), nullable=False)
    participation_score = Column(Float, default=0.0)
    rewards_earned = Column(JSON, default=dict)  # {artifacts: [], stellar_shards: 0, xp: 0}
    participated_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="anomaly_participations")
    event = relationship("QuantumAnomalyEvent", back_populates="participations")


# Cosmic Genesis Grid Models
class CosmicGenesisTile(Base):
    __tablename__ = "cosmic_genesis_tiles"
    
    id = Column(Integer, primary_key=True, index=True)
    tile_id = Column(String, unique=True, nullable=False)  # e.g., "stellar_forge_1"
    name = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    tile_type = Column(String, nullable=False)  # upgrade, multiplier, efficiency, special
    category = Column(String, nullable=False)  # stellar_forge, cosmic_market, etc.
    
    # Position in grid
    grid_x = Column(Integer, nullable=False)
    grid_y = Column(Integer, nullable=False)
    
    # Costs and effects
    base_cost = Column(Float, nullable=False)
    cost_scaling = Column(Float, default=1.1)
    effect_description = Column(Text, nullable=False)
    effect_data = Column(JSON, default=dict)  # {type: "multiplier", value: 1.5, target: "xp"}
    
    # Prerequisites
    prerequisite_tiles = Column(JSON, default=list)  # List of tile_ids that must be unlocked first
    min_level = Column(Integer, default=1)
    min_ascension_tier = Column(Integer, default=0)


class UserCosmicProgress(Base):
    __tablename__ = "user_cosmic_progress"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    tile_id = Column(String, ForeignKey("cosmic_genesis_tiles.tile_id"), nullable=False)
    unlock_level = Column(Integer, default=0)
    total_invested = Column(Float, default=0.0)
    unlocked_at = Column(DateTime, default=datetime.utcnow)
    last_upgraded_at = Column(DateTime, nullable=True)
    
    # Current effects
    current_effect_multiplier = Column(Float, default=1.0)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    user = relationship("User", back_populates="cosmic_progress")
    tile = relationship("CosmicGenesisTile")


# Enhanced User Model Extensions
class UserGameStats(Base):
    __tablename__ = "user_game_stats"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Currency balances
    stellar_shards = Column(Float, default=0.0)
    lumina = Column(Float, default=0.0)
    stardust = Column(Float, default=0.0)
    
    # Trading statistics
    total_trades = Column(Integer, default=0)
    successful_trades = Column(Integer, default=0)
    total_profit_loss = Column(Float, default=0.0)
    best_trade_profit = Column(Float, default=0.0)
    worst_trade_loss = Column(Float, default=0.0)
    
    # Streaks and achievements
    current_streak = Column(Integer, default=0)
    best_streak = Column(Integer, default=0)
    last_trade_date = Column(DateTime, nullable=True)
    
    # Game progression
    cosmic_tier = Column(Integer, default=0)
    total_artifacts_discovered = Column(Integer, default=0)
    total_anomalies_participated = Column(Integer, default=0)
    total_lottery_tickets_bought = Column(Integer, default=0)
    
    # Multipliers (calculated from all sources)
    total_xp_multiplier = Column(Float, default=1.0)
    total_earning_multiplier = Column(Float, default=1.0)
    total_luck_multiplier = Column(Float, default=1.0)
    
    # Relationships
    user = relationship("User", back_populates="game_stats")


# Add these relationships to the existing User model
# This would be added to database.py User class:
"""
# Add these to the User class in database.py:
artifacts = relationship("Artifact", back_populates="user")
ascension_tier = relationship("AscensionTier", back_populates="user", uselist=False)
lottery_tickets = relationship("LotteryTicket", back_populates="user")
shield_dust = relationship("ShieldDust", back_populates="user", uselist=False)
anomaly_participations = relationship("AnomalyParticipation", back_populates="user")
cosmic_progress = relationship("UserCosmicProgress", back_populates="user")
game_stats = relationship("UserGameStats", back_populates="user", uselist=False)
"""

# Constellation Clan System Models
class Constellation(Base):
    __tablename__ = "constellations"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Constellation stats
    member_count = Column(Integer, default=0)
    total_stellar_shards = Column(Float, default=0.0)
    total_lumina = Column(Float, default=0.0)
    constellation_level = Column(Integer, default=1)
    
    # Visual and social features
    constellation_color = Column(String(7), default="#7B2CBF")  # Hex color
    constellation_emblem = Column(String(50), default="star")  # Icon identifier
    is_public = Column(Boolean, default=True)
    max_members = Column(Integer, default=50)
    
    # Battle and competition stats
    total_battles = Column(Integer, default=0)
    battles_won = Column(Integer, default=0)
    battle_rating = Column(Float, default=1000.0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    owner = relationship("User", back_populates="owned_constellation")
    members = relationship("ConstellationMembership", back_populates="constellation")
    challenger_battles = relationship("ConstellationBattle", foreign_keys="ConstellationBattle.challenger_constellation_id", back_populates="challenger_constellation")
    defender_battles = relationship("ConstellationBattle", foreign_keys="ConstellationBattle.defender_constellation_id", back_populates="defender_constellation")


class ConstellationMembership(Base):
    __tablename__ = "constellation_memberships"
    
    id = Column(Integer, primary_key=True, index=True)
    constellation_id = Column(Integer, ForeignKey("constellations.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Member role and permissions
    role = Column(String(20), default="member")  # owner, admin, member
    contribution_score = Column(Integer, default=0)
    
    # Member stats within constellation
    stellar_shards_contributed = Column(Float, default=0.0)
    lumina_contributed = Column(Float, default=0.0)
    battles_participated = Column(Integer, default=0)
    
    # Status and timestamps
    is_active = Column(Boolean, default=True)
    joined_at = Column(DateTime, default=datetime.utcnow)
    last_active_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    constellation = relationship("Constellation", back_populates="members")
    user = relationship("User", back_populates="constellation_membership")


class ConstellationBattle(Base):
    __tablename__ = "constellation_battles"
    
    id = Column(Integer, primary_key=True, index=True)
    challenger_constellation_id = Column(Integer, ForeignKey("constellations.id"), nullable=False)
    defender_constellation_id = Column(Integer, ForeignKey("constellations.id"), nullable=False)
    
    # Battle configuration
    battle_type = Column(String(50), nullable=False)  # trading_duel, stellar_supremacy, cosmic_conquest
    duration_hours = Column(Integer, default=24)
    
    # Battle status
    status = Column(String(20), default="pending")  # pending, active, completed, cancelled
    winner_constellation_id = Column(Integer, ForeignKey("constellations.id"), nullable=True)
    
    # Battle metrics
    challenger_score = Column(Float, default=0.0)
    defender_score = Column(Float, default=0.0)
    total_participants = Column(Integer, default=0)
    
    # Rewards and prizes
    prize_pool = Column(Float, default=0.0)
    winner_reward = Column(Float, default=0.0)
    rewards_distributed = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    challenger_constellation = relationship("Constellation", foreign_keys=[challenger_constellation_id], back_populates="challenger_battles")
    defender_constellation = relationship("Constellation", foreign_keys=[defender_constellation_id], back_populates="defender_battles")
    winner_constellation = relationship("Constellation", foreign_keys=[winner_constellation_id])
    participations = relationship("ConstellationBattleParticipation", back_populates="battle")


class ConstellationBattleParticipation(Base):
    __tablename__ = "constellation_battle_participations"
    
    id = Column(Integer, primary_key=True, index=True)
    battle_id = Column(Integer, ForeignKey("constellation_battles.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    constellation_id = Column(Integer, ForeignKey("constellations.id"), nullable=False)
    
    # Participation metrics
    individual_score = Column(Float, default=0.0)
    trades_completed = Column(Integer, default=0)
    stellar_shards_earned = Column(Float, default=0.0)
    contribution_percentage = Column(Float, default=0.0)
    
    # Rewards
    individual_reward = Column(Float, default=0.0)
    bonus_xp = Column(Integer, default=0)
    
    # Timestamps
    joined_at = Column(DateTime, default=datetime.utcnow)
    last_activity_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    battle = relationship("ConstellationBattle", back_populates="participations")
    user = relationship("User", back_populates="battle_participations")
    constellation = relationship("Constellation")


# Social Prestige System Models
class UserPrestige(Base):
    __tablename__ = "user_prestige"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    
    # Verification system
    is_verified = Column(Boolean, default=False)
    verification_tier = Column(Integer, default=0)  # 0-3 (None, Bronze, Silver, Gold)
    verification_date = Column(DateTime, nullable=True)
    
    # Prestige display
    spotlight_eligible = Column(Boolean, default=False)
    aura_color = Column(String(7), default="#FFFFFF")  # Hex color for verified aura
    custom_title = Column(String(100), nullable=True)
    badge_collection = Column(JSON, default=list)  # List of earned badges
    
    # Spotlight system
    spotlight_count = Column(Integer, default=0)
    last_spotlight_date = Column(DateTime, nullable=True)
    spotlight_votes = Column(Integer, default=0)
    
    # Social metrics
    social_rating = Column(Float, default=0.0)
    influence_score = Column(Float, default=0.0)
    community_contributions = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="prestige")


# Viral Content System Models
class ViralContent(Base):
    __tablename__ = "viral_content"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Content details
    content_type = Column(String(50), nullable=False)  # meme, snapshot, achievement, nft
    content_title = Column(String(200), nullable=False)
    content_description = Column(Text, nullable=True)
    content_data = Column(JSON, nullable=False)  # Meme template, screenshot data, etc.
    
    # Sharing and viral metrics
    share_count = Column(Integer, default=0)
    viral_score = Column(Integer, default=0)
    engagement_rate = Column(Float, default=0.0)
    platform_shares = Column(JSON, default=dict)  # {twitter: 5, instagram: 3, etc.}
    
    # Content metadata
    template_id = Column(String(50), nullable=True)  # For memes
    trading_context = Column(JSON, nullable=True)  # Associated trading data
    achievement_context = Column(JSON, nullable=True)  # Associated achievements
    
    # Status and visibility
    is_public = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False)
    moderation_status = Column(String(20), default="approved")  # pending, approved, rejected
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    last_shared_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="viral_content")


# FOMO Events System Models
class FOMOEvent(Base):
    __tablename__ = "fomo_events"
    
    id = Column(Integer, primary_key=True, index=True)
    event_name = Column(String(100), nullable=False)
    event_type = Column(String(50), nullable=False)  # limited_nft, bonus_multiplier, exclusive_feature
    description = Column(Text, nullable=False)
    
    # Event configuration
    max_participants = Column(Integer, nullable=True)
    participation_requirements = Column(JSON, default=dict)  # {min_level: 5, min_trades: 10}
    
    # Event rewards
    reward_type = Column(String(50), nullable=False)  # nft, stellar_shards, lumina, badge
    reward_data = Column(JSON, nullable=False)  # Specific reward configuration
    
    # Timing and urgency
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    urgency_level = Column(Integer, default=1)  # 1-5 (low to extreme urgency)
    
    # Progress tracking
    current_participants = Column(Integer, default=0)
    completion_threshold = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True)
    is_completed = Column(Boolean, default=False)
    
    # Relationships
    participations = relationship("FOMOEventParticipation", back_populates="event")


class FOMOEventParticipation(Base):
    __tablename__ = "fomo_event_participations"
    
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("fomo_events.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Participation details
    participation_score = Column(Float, default=0.0)
    requirements_met = Column(JSON, default=dict)  # Which requirements were satisfied
    
    # Rewards
    reward_earned = Column(Boolean, default=False)
    reward_claimed = Column(Boolean, default=False)
    reward_data = Column(JSON, nullable=True)  # Specific reward details
    
    # Timestamps
    joined_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    event = relationship("FOMOEvent", back_populates="participations")
    user = relationship("User", back_populates="fomo_participations")
