import pytest
from unittest.mock import patch
from src.app import app

# --- SETUP ---
@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client
# -------------

@pytest.mark.buttons
def test_pull_data_success(client):
    """Test that the pull-data button works."""
    # We fake the scraper so it doesn't go to the real internet
    with patch('src.app.scrape_grad_cafe') as mock_scrape: 
        response = client.post('/pull-data')
        assert response.status_code == 200

@pytest.mark.buttons
def test_busy_gating(client):
    """Test that the app blocks requests when busy."""
    # Fake being 'busy'
    with client.session_transaction() as sess:
        sess['is_pulling'] = True
    
    response = client.post('/pull-data')
    assert response.status_code == 409  # 409 = Conflict (Busy)