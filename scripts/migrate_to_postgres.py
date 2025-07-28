#!/usr/bin/env python3
"""
Migrate from SQLite to PostgreSQL
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, User, Trade, ApiKey
from game_models import *

def migrate_database():
    # Source (SQLite)
    sqlite_engine = create_engine("sqlite:///./astratrade.db")
    SqliteSession = sessionmaker(bind=sqlite_engine)
    sqlite_session = SqliteSession()
    
    # Destination (PostgreSQL)
    postgres_url = os.getenv("DATABASE_URL", "postgresql://astratrade:astratrade123@localhost:5432/astratrade")
    postgres_engine = create_engine(postgres_url)
    PostgresSession = sessionmaker(bind=postgres_engine)
    postgres_session = PostgresSession()
    
    # Create all tables in PostgreSQL
    Base.metadata.create_all(bind=postgres_engine)
    
    # Migrate each table
    tables = [User, Trade, ApiKey, Artifact, AscensionTier, LotteryRound, LotteryTicket, 
              ShieldDust, QuantumAnomaly, CosmicGenesisTile, UserGameStats]
    
    for table in tables:
        print(f"Migrating {table.__tablename__}...")
        records = sqlite_session.query(table).all()
        for record in records:
            postgres_session.merge(record)
        postgres_session.commit()
        print(f"  Migrated {len(records)} records")
    
    print("Migration complete!")

if __name__ == "__main__":
    migrate_database()
