import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.main import app
from app.db import Base, get_session

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=False)

@pytest.fixture(autouse=True)
async def prepare_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
async def client():
    async def override_get_session():
        async with TestingSessionLocal() as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
        
    app.dependency_overrides.clear()


@pytest.fixture
async def chief_client(client):
    await client.post("/auth/register", json={
        "email": "chief@example.com",
        "name": "Chief",
        "password": "password",
        "role": "chief"
    })
    await client.post("/auth/login", json={
        "email": "chief@example.com",
        "password": "password"
    })
    return client


@pytest.fixture
async def member_client(client):
    await client.post("/auth/register", json={
        "email": "member@example.com",
        "name": "Member",
        "password": "password",
        "role": "member"
    })
    await client.post("/auth/login", json={
        "email": "member@example.com",
        "password": "password"
    })
    return client
