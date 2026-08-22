import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.api import APPROVALS, EVIDENCE, REQUESTS, EVENTS, reset_state if False else None
