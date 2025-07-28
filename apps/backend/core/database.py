from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
from datetime import datetime
from .config import Settings

# Database setup
settings = Settings()
engine = create_engine(settings.DATABASE_URL, echo=settings.DEBUG)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Database Models
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=True)
    hashed_password = Column(String, nullable=False)
    xp = Column(Integer, default=0)
    level = Column(Integer, default=1)
    wallet_address = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Game system relationships
    artifacts = relationship("Artifact", back_populates="user")
    ascension_tier = relationship("AscensionTier", back_populates="user", uselist=False)
    lottery_tickets = relationship("LotteryTicket", back_populates="user")
    shield_dust = relationship("ShieldDust", back_populates="user", uselist=False)
    anomaly_participations = relationship("AnomalyParticipation", back_populates="user")
    cosmic_progress = relationship("UserCosmicProgress", back_populates="user")
    game_stats = relationship("UserGameStats", back_populates="user", uselist=False)
    
    # Phase 3 Social Features relationships
    owned_constellation = relationship("Constellation", back_populates="owner", uselist=False)
    constellation_membership = relationship("ConstellationMembership", back_populates="user", uselist=False)
    battle_participations = relationship("ConstellationBattleParticipation", back_populates="user")
    prestige = relationship("UserPrestige", back_populates="user", uselist=False)
    viral_content = relationship("ViralContent", back_populates="user")
    fomo_participations = relationship("FOMOEventParticipation", back_populates="user")


class Trade(Base):
    __tablename__ = "trades"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    asset = Column(String, nullable=False)
    direction = Column(String, nullable=False)  # 'long' or 'short'
    amount = Column(Float, nullable=False)
    entry_price = Column(Float, nullable=True)
    exit_price = Column(Float, nullable=True)
    profit_loss = Column(Float, default=0.0)
    profit_percentage = Column(Float, default=0.0)
    status = Column(String, default="pending")  # pending, completed, cancelled
    xp_gained = Column(Integer, default=0)
    is_real_trade = Column(Boolean, default=False)
    stellar_shards_earned = Column(Float, default=0.0)
    lumina_earned = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    # Game system relationships
    shield_protection = relationship(
        "ShieldProtectionEvent", back_populates="trade", uselist=False
    )


class ApiKey(Base):
    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    exchange = Column(String, nullable=False)
    encrypted_api_key = Column(String, nullable=False)
    encrypted_secret_key = Column(String, nullable=False)
    encrypted_passphrase = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Create tables
def create_tables():
    Base.metadata.create_all(bind=engine)
