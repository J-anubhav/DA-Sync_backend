from typing import AsyncGenerator
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo import MongoClient
import certifi

try:
    from .config import settings
except ImportError:
    from config import settings

_client: AsyncIOMotorClient | None = None
_db: AsyncIOMotorDatabase | None = None

async def get_client() -> AsyncIOMotorClient:
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(settings.mongo_uri, tlsCAFile=certifi.where())
    return _client

async def get_db() -> AsyncGenerator[AsyncIOMotorDatabase, None]:
    global _db
    if _db is None:
        client = await get_client()
        _db = client[settings.mongo_db_name]
    assert _db is not None
    yield _db

# Synchronous client for background tasks
_sync_client: MongoClient | None = None

def get_sync_client() -> MongoClient:
    global _sync_client
    if _sync_client is None:
        _sync_client = MongoClient(settings.mongo_uri, tlsCAFile=certifi.where())
    return _sync_client

_sync_db = get_sync_client()[settings.mongo_db_name]
prescription_collection = _sync_db["prescriptions"]