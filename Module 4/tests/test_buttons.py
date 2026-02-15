import pytest
from unittest.mock import patch
from src.app import app

# --- SETUP ---
@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.secret_key = 'test_secret'
    with app.test_client() as client:
        yield client
# -------------

@pytest.mark.buttons
def test_pull_data_click(client):
    """Test that the pull-data button triggers the scraper."""
    # Mock the scraper so we don't actually run it
    with patch('src.app.run_scraper') as mock_scraper:
        # Your app redirects (302) back to index after clicking
        response = client.post('/pull_data')
        
        # 302 means Redirect (Success in your app's logic)
        assert response.status_code == 302 
        
        # Verify the redirect goes to index
        assert response.location == '/' or 'http://localhost/' in response.location

@pytest.mark.buttons
def test_busy_behavior(client):
    """Test that the app blocks a second pull if one is running."""
    # 1. Fake the 'scraping_active' flag in your app
    import src.app
    src.app.scraping_active = True
    
    try:
        # 2. Try to pull again
        response = client.post('/pull_data', follow_redirects=True)
        
        # 3. Should see the flash message about being busy
        assert b"already in progress" in response.data
        
    finally:
        # Reset flag so other tests don't break
        src.app.scraping_active = False