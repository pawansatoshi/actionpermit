from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_healthz():
    response = client.get('/healthz')
    assert response.status_code == 200
    assert response.json() == {'status': 'ok'}


def test_readyz():
    response = client.get('/readyz')
    assert response.status_code == 200
    assert response.json() == {'status': 'ready'}


def test_root_serves_frontend():
    response = client.get('/')
    assert response.status_code == 200
    assert 'ActionPermit' in response.text
