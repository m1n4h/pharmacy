"""
Test Configuration and Fixtures
PharmaMonitor - Complete Testing Suite
"""
import os
import sys
import pytest

# Disable rate limiting for tests
os.environ["TESTING"] = "1"

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Add the backend directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.base_class import Base
from app.db.session import SessionLocal
from app.models import *  # noqa: F401, F403 — ensure all models are registered
from app.services.permission_service import PermissionService


# ---- Database Fixtures ----

@pytest.fixture(scope="session")
def test_db_url():
    """Use a dedicated test database."""
    return os.environ.get(
        "TEST_DATABASE_URL",
        "postgresql://postgres:egovridc@localhost:5432/pharmacy_test"
    )


@pytest.fixture(scope="session")
def engine(test_db_url):
    """Create the test engine and build all tables."""
    eng = create_engine(test_db_url, pool_pre_ping=True)
    Base.metadata.create_all(bind=eng)
    yield eng
    # Cleanup: drop all tables after session
    Base.metadata.drop_all(bind=eng)
    eng.dispose()


@pytest.fixture(scope="function")
def db(engine):
    """Provide a transactional session for each test, rolled back after."""
    connection = engine.connect()
    transaction = connection.begin()
    session = SessionLocal(bind=connection)
    try:
        PermissionService.initialize(session)
        # Seed settings if not present
        from app.models.settings import Settings
        if not session.query(Settings).filter(Settings.id == 1).first():
            session.add(Settings(id=1, pharmacy_name="Test Pharmacy"))
            session.commit()
        # Seed currencies if not present
        from app.models.currency import Currency
        if not session.query(Currency).first():
            session.add(Currency(code="TZS", name="Tanzanian Shilling", symbol="TSh", rate_to_tzs=1.0))
            session.add(Currency(code="USD", name="US Dollar", symbol="$", rate_to_tzs=2500.0))
            session.add(Currency(code="EUR", name="Euro", symbol="€", rate_to_tzs=2700.0))
            session.commit()
        # Seed superadmin user if not present
        from app.models.user import User
        from app.core.security import hash_password
        if not session.query(User).filter(User.email == "changwamale48@gmail.com").first():
            session.add(User(
                email="changwamale48@gmail.com",
                full_name="Super Admin",
                hashed_password=hash_password("ngwamale#@39"),
                role="superadmin",
                is_active=1,
                is_superuser=1,
            ))
            session.commit()
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture(scope="function")
def client(db):
    """Provide a FastAPI TestClient that uses the same DB session as `db`."""
    from fastapi.testclient import TestClient
    from app.main import app
    from app.db.db import get_db

    def _override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


# ---- Auth Fixtures ----

@pytest.fixture(scope="function")
def superadmin_token(client):
    """Login as superadmin and return the JWT token."""
    res = client.post("/auth/login", json={
        "email": "changwamale48@gmail.com",
        "password": "ngwamale#@39"
    })
    assert res.status_code == 200, f"Login failed: {res.json()}"
    return res.json()["data"]["access_token"]


@pytest.fixture(scope="function")
def auth_headers(superadmin_token):
    """Return Authorization headers dict for superadmin."""
    return {"Authorization": f"Bearer {superadmin_token}"}


@pytest.fixture(scope="function")
def test_user(db):
    """Create a test staff user in the DB."""
    from app.services.user_service import UserService
    user, err = UserService.create_user(
        db,
        email="testuser@pharmacy.com",
        password="TestPass123!",
        full_name="Test Staff",
        role="staff"
    )
    assert user is not None, f"Create user failed: {err}"
    return user


@pytest.fixture(scope="function")
def test_staff_token(client, test_user):
    """Login as the test staff user and return JWT token."""
    res = client.post("/auth/login", json={
        "email": "testuser@pharmacy.com",
        "password": "TestPass123!"
    })
    assert res.status_code == 200, f"Staff login failed: {res.json()}"
    return res.json()["data"]["access_token"]


@pytest.fixture(scope="function")
def staff_headers(test_staff_token):
    """Return Authorization headers dict for staff user."""
    return {"Authorization": f"Bearer {test_staff_token}"}
