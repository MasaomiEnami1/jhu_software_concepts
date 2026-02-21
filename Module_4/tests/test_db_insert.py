import pytest
from unittest.mock import MagicMock, patch
from src.app import app, get_db_connection, get_val

@pytest.mark.db
def test_database_connection_success():
    """Test that the app connects to the DB correctly."""
    with patch('psycopg2.connect') as mock_connect:
        conn = get_db_connection()
        assert mock_connect.called
        assert conn is not None

@pytest.mark.db
def test_database_connection_failure():
    """Test that the app handles DB connection errors gracefully."""
    # Force connection to fail
    with patch('psycopg2.connect', side_effect=Exception("Connection Failed")):
        conn = get_db_connection()
        assert conn is None # Should return None, not crash

@pytest.mark.db
def test_get_val_success():
    """Test the helper function that runs SQL queries."""
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = [99] # Fake result
    mock_conn = MagicMock()

    result = get_val(mock_cursor, mock_conn, "SELECT COUNT(*) FROM table")
    assert result == 99

@pytest.mark.db
def test_get_val_failure():
    """Test that get_val returns 0 on SQL error."""
    mock_cursor = MagicMock()
    # Force an error
    mock_cursor.execute.side_effect = Exception("SQL Error")
    mock_conn = MagicMock()

    result = get_val(mock_cursor, mock_conn, "SELECT * FROM table")
    assert result == 0
    mock_conn.rollback.assert_called()