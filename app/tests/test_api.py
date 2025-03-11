import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import create_engine

from app.main import Base, app, get_db


TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
test_engine = create_async_engine(TEST_DATABASE_URL, future=True, echo=False)
sync_test_engine = create_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = async_sessionmaker(test_engine, expire_on_commit=False, class_=AsyncSession)

async def override_get_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with TestSessionLocal() as session:
        yield session

app.dependency_overrides[get_db] = override_get_db

@pytest.mark.asyncio
async def test_add_wallet():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/api/v1/wallets/add")

    assert response.status_code == 200
    data = response.json()
    assert "uuid" in data
    assert data["balance"] == 0

@pytest.mark.asyncio
async def test_get_wallet():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        create_response = await ac.post("/api/v1/wallets/add")
        wallet_data = create_response.json()

        response = await ac.get(f"/api/v1/wallets/{wallet_data['uuid']}")
        assert response.status_code == 200
        data = response.json()
        assert data["uuid"] == wallet_data["uuid"]
        assert data["balance"] == 0

@pytest.mark.asyncio
async def test_wallet_operations():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        create_response = await ac.post("/api/v1/wallets/add")
        wallet_data = create_response.json()
        wallet_uuid = wallet_data["uuid"]

        deposit_response = await ac.post(
            f"/api/v1/wallets/{wallet_uuid}/operation",
            json={"operation_type": "DEPOSIT", "amount": 100}
        )
        assert deposit_response.status_code == 200
        assert deposit_response.json()["balance"] == 100

        withdraw_response = await ac.post(
            f"/api/v1/wallets/{wallet_uuid}/operation",
            json={"operation_type": "WITHDRAW", "amount": 50}
        )
        assert withdraw_response.status_code == 200
        assert withdraw_response.json()["balance"] == 50

        insufficient_funds_response = await ac.post(
            f"/api/v1/wallets/{wallet_uuid}/operation",
            json={"operation_type": "WITHDRAW", "amount": 100}
        )
        assert insufficient_funds_response.status_code == 400
        assert insufficient_funds_response.json()["detail"] == "Insufficient funds"

@pytest.mark.asyncio
async def test_wallet_not_found():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/v1/wallets/550e8400-e29b-41d4-a716-446655440000")
        assert response.status_code == 404
        assert response.json()["detail"] == "Wallet not found"
