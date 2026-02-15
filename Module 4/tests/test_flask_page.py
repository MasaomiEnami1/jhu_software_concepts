import pytest
from src.app import app  # Import your actual Flask app

# --- SETUP (The code that replaces conftest.py) ---
@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client
# --------------------------------------------------

@pytest.mark.web
def test_analysis_page_loads(client):
    """Test that the analysis page loads successfully."""
    response = client.get('/analysis')
    assert response.status_code == 200

@pytest.mark.web
def test_page_text(client):
    """Test that the page contains the correct text."""
    response = client.get('/analysis')
    html = response.data.decode('utf-8')
    assert "Pull Data" in html
    assert "Update Analysis" in html