import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from astratrade_backend.core.database import Base, get_db, User
from astratrade_backend.core.main import app
from astratrade_backend.auth.auth import get_password_hash

# Test database
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test_astratrade.db"

@pytest.fixture(scope="session")
def test_db():
    engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    yield TestingSessionLocal()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client(test_db):
    def override_get_db():
        yield test_db
    
    app.dependency_overrides[get_db] = override_get_db
    from fastapi.testclient import TestClient
    yield TestClient(app)
    app.dependency_overrides.clear()

@pytest.fixture
def test_user(test_db):
    user = test_db.query(User).filter_by(username="testuser").first()
    if user:
        return user
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=get_password_hash("testpass123"),
        xp=100,
        level=2
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user
