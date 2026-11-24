from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import create_app
from app.models import Impianto, Prezzo, User, UserRole
from app.security import hash_password


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestSession = sessionmaker(bind=test_engine, autoflush=False, expire_on_commit=False)
    app = create_app(database_engine=test_engine)

    def override_db():
        db = TestSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_db
    with TestClient(app) as test_client:
        with TestSession() as db:
            db.add_all([
                User(
                    email="driver@example.invalid", display_name="Driver Demo",
                    password_hash=hash_password("Driver-Password-123"),
                    role=UserRole.AUTOMOBILISTA,
                ),
                User(
                    email="admin@example.invalid", display_name="Admin Demo",
                    password_hash=hash_password("Admin-Password-123"),
                    role=UserRole.ADMIN,
                ),
            ])
            db.flush()
            station = Impianto(
                id_impianto="TEST-001", gestore="Test", bandiera="Demo",
                tipo_impianto="Stradale", nome="Stazione Test", indirizzo="Via Finta 1",
                comune="Torino", provincia="TO",
            )
            db.add(station)
            db.flush()
            db.add(Prezzo(
                id_impianto=station.id, carburante="Benzina", prezzo=1.75, is_self=True
            ))
            db.commit()
        yield test_client
    app.dependency_overrides.clear()
    Base.metadata.drop_all(test_engine)
    test_engine.dispose()
