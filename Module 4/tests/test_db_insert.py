import pytest
from unittest.mock import MagicMock, patch
from src.app import app, get_db_connection, get_val

# --- SETUP ---
@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

# --- TESTS ---

@pytest.mark.db
def test_database_connection_success():
    """Test that the app connects to the DB correctly."""
    with patch('src.app.psycopg2.connect') as mock_connect:
        conn = get_db_connection()
        assert mock_connect.called
        assert conn is not None

@pytest.mark.db
def test_database_connection_failure():
    """Test that the app handles DB connection errors gracefully."""
    # We force the connection to crash to test the 'except' block in app.py
    with patch('src.app.psycopg2.connect', side_effect=Exception("Connection Failed")):
        conn = get_db_connection()
        assert conn is None  # app.py should return None, not crash

@pytest.mark.db
def test_get_val_success():
    """Test that the helper function runs queries correctly."""
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = [100] # Fake result
    mock_conn = MagicMock()

    result = get_val(mock_cursor, mock_conn, "SELECT COUNT(*) FROM table")
    assert result == 100

@pytest.mark.db
def test_get_val_failure():
    """Test that the helper function returns 0 if the query fails."""
    mock_cursor = MagicMock()
    mock_cursor.execute.side_effect = Exception("SQL Error") # Force crash
    mock_conn = MagicMock()

    result = get_val(mock_cursor, mock_conn, "SELECT BAD SQL")
    
    assert result == 0 # app.py should catch the error and return 0
    mock_conn.rollback.assert_called() # It should also rollback the DB