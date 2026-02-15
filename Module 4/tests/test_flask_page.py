import pytest
from src.app import app

# --- SETUP ---
@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client
# -------------

@pytest.mark.web
def test_home_page_loads(client):
    """Test that the home page loads successfully."""
    # Your analysis is on the home page '/'
    with client.session_transaction() as sess:
        # Mock session to avoid errors
        sess['scraping_status'] = False
        
    response = client.get('/') 
    assert response.status_code == 200

@pytest.mark.web
def test_page_buttons(client):
    """Test that the page contains the Pull Data button."""
    response = client.get('/')
    html = response.data.decode('utf-8')
    
    # Check for the form action="/pull_data"
    assert 'action="/pull_data"' in html or "pull_data" in html
    # Check for the update analysis link
    assert "update_analysis" in html