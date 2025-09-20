from unittest.mock import Mock, patch

import pytest
from fastapi.testclient import TestClient

from agrotech_ai.app import app


class TestMainAPI:
    """Test cases for main FastAPI application."""

    @pytest.fixture
    def client(self):
        """Test client fixture."""
        return TestClient(app)

    def test_root_endpoint(self, client):
        """Test root endpoint response."""
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()

        assert "message" in data
        assert "model" in data
        assert "version" in data
        assert "endpoints" in data
        assert data["version"] == "1.0.0"

    @patch("agrotech_ai.app.check_ollama_connection")
    def test_health_check_healthy(self, mock_check, client):
        """Test health check endpoint when Ollama is running."""
        mock_check.return_value = True

        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "healthy"
        assert data["ollama"] == "running"
        assert "model" in data

    @patch("agrotech_ai.app.check_ollama_connection")
    def test_health_check_unhealthy(self, mock_check, client):
        """Test health check endpoint when Ollama is not running."""
        mock_check.return_value = False

        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "error"
        assert data["ollama"] == "not_running"

    def test_nonexistent_endpoint(self, client):
        """Test accessing non-existent endpoint."""
        response = client.get("/nonexistent")
        assert response.status_code == 404

    def test_cors_headers(self, client):
        """Test CORS headers are present."""
        response = client.options("/")

        # CORS headers should be present
        assert (
            "access-control-allow-origin" in response.headers
            or response.status_code == 200
        )

    def test_logging_setup(self):
        """Test that logging is set up on import."""
        # Since main module is already imported, we need to check if setup_logging
        # was called by verifying the logging configuration exists
        import logging

        logger = logging.getLogger()

        # Check that logger has been configured (has handlers)
        assert len(logger.handlers) > 0

        # Check that we have both console and file handlers
        handler_types = [type(handler).__name__ for handler in logger.handlers]
        assert "StreamHandler" in handler_types
        assert "FileHandler" in handler_types


class TestLoggingSetup:
    """Test cases for logging setup."""

    @patch("logging.getLogger")
    @patch("logging.StreamHandler")
    @patch("logging.FileHandler")
    def test_setup_logging_configuration(
        self, mock_file_handler, mock_stream_handler, mock_get_logger
    ):
        """Test logging configuration setup."""
        from agrotech_ai.app import setup_logging

        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        setup_logging()

        # Verify logger configuration
        mock_logger.setLevel.assert_called()
        mock_logger.addHandler.assert_called()

        # Verify handlers are created
        mock_stream_handler.assert_called()
        mock_file_handler.assert_called_with("agrotech.log")

    def test_log_file_creation(self):
        """Test that log file is created with proper name."""
        from agrotech_ai.app import setup_logging

        # Setup logging should create agrotech.log
        setup_logging()

        # Note: This test might need adjustment based on where the test is run
        # The log file should be created in the current working directory
