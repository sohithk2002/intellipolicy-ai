"""Shared pytest fixtures for IntelliPolicy AI backend tests."""
import sys
from pathlib import Path
import pytest
from starlette.testclient import TestClient

# Make sure `backend/` is on the path so `import main` works
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from main import app  # noqa: E402


@pytest.fixture(scope="session")
def client() -> TestClient:
    with TestClient(app) as c:
        yield c
