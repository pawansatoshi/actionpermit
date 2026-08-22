from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_healthz():
    response = client.get('/healthz', headers={'X-Request-ID': 'health-test-1'})
    assert response.status_code == 200
    assert response.json() == {'status': 'ok'}
    assert response.headers['X-Request-ID'] == 'health-test-1'
    assert response.headers['X-Content-Type-Options'] == 'nosniff'
    assert response.headers['X-Frame-Options'] == 'DENY'


def test_readyz():
    response = client.get('/readyz')
    assert response.status_code == 200
    assert response.json() == {'status': 'ready'}
    assert response.headers.get('X-Request-ID')


def test_root_serves_frontend():
    response = client.get('/')
    assert response.status_code == 200
    assert 'ActionPermit' in response.text
