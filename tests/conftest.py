import os
import sys
from pathlib import Path

# Ensure imports that initialize SQLAlchemy use an in-memory database during tests.
os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")
# Ensure local packages (e.g., backend/) are importable during pytest collection.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest

import backend.models  # noqa: F401 - imports model metadata
from backend.db import Base, SessionLocal, engine


@pytest.fixture(autouse=True)
def reset_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
