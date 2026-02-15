import pytest

@pytest.mark.analysis
def test_percentage_formatting():
    """Test that percentages show 2 decimal places."""
    # You can test your specific logic here
    number = 0.123456
    formatted = f"{number * 100:.2f}%"
    assert formatted == "12.35%"

@pytest.mark.analysis
def test_answer_label(client): # If you need client here, copy the setup fixture again
    from src.app import app
    app.config['TESTING'] = True
    client = app.test_client()
    
    response = client.get('/analysis')
    assert b"Answer:" in response.data