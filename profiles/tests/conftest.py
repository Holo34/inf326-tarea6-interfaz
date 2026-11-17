import os
import pytest
from fastapi.testclient import TestClient
import mongomock
from unittest.mock import patch

# Configuramos entorno de prueba antes de importar la app
os.environ["MONGODB_URL"] = "mongodb://localhost:27017"
os.environ["USERS_URL"] = "http://users-mock:8000"

# Parcheamos MongoClient globalmente en main antes de importar app
with patch("pymongo.MongoClient", new=mongomock.MongoClient):
    from app.main import app, database, AVATARS_DIR

@pytest.fixture(autouse=True)
def clear_db():
    """Limpia la base de datos antes de cada prueba para mantener el aislamiento."""
    database.profiles.drop()
    yield

@pytest.fixture
def client():
    return TestClient(app)