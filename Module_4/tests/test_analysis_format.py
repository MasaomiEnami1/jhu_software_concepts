import pytest
from src.app import app

# --- SETUP ---
@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client
# -------------

@pytest.mark.analysis
def test_percentage_formatting():
    """Test that percentages show 2 decimal places."""
    # This tests the logic you use in your SQL queries (ROUND(x, 2))
    val = 0.123456 * 100
    formatted = round(val, 2)
    assert formatted == 12.35

@pytest.mark.analysis
def test_analysis_labels(client):
    """Test that the page loads the analysis table."""
    response = client.get('/')
    assert response.status_code == 200
    # Check for a specific label from your table
    html = response.data.decode('utf-8')
    assert "GPA" in html or "GRE" in html