import pytest
from unittest.mock import Mock, patch, MagicMock
import json
from ollama_client import (
    OllamaAgent,
    get_shared_session,
    reset_shared_session
)


class TestOllamaAgent:
    """Test cases for OllamaAgent base class."""

    def test_agent_initialization(self):
        """Test agent initialization with role and expertise."""
        agent = OllamaAgent("TestRole", "test expertise")
        assert agent.role == "TestRole"
        assert agent.expertise == "test expertise"
        assert agent.session is not None

    @pytest.mark.asyncio
    async def test_generate_response_success(self, mock_requests_session):
        """Test successful response generation."""
        agent = OllamaAgent("TestAgent", "testing")
        agent.session = mock_requests_session

        result = await agent.generate_response("test prompt")

        mock_requests_session.post.assert_called_once()
        assert isinstance(result, dict)
        assert "test" in result

    @pytest.mark.asyncio
    async def test_generate_response_http_error(self, mock_requests_session):
        """Test response generation with HTTP error."""
        agent = OllamaAgent("TestAgent", "testing")
        agent.session = mock_requests_session
        mock_requests_session.post.return_value.status_code = 500

        result = await agent.generate_response("test prompt")

        # Should return fallback response
        assert isinstance(result, dict)
        assert "error" in result

    @pytest.mark.asyncio
    async def test_generate_response_connection_error(self):
        """Test response generation with connection error."""
        agent = OllamaAgent("TestAgent", "testing")
        agent.session = Mock()
        agent.session.post.side_effect = Exception("Connection failed")

        result = await agent.generate_response("test prompt")

        # Should return fallback response
        assert isinstance(result, dict)
        assert "error" in result

    def test_parse_json_response_valid(self):
        """Test parsing valid JSON response."""
        agent = OllamaAgent("TestAgent", "testing")
        json_string = '{"key": "value", "number": 42}'

        result = agent._parse_json_response(json_string)

        assert result == {"key": "value", "number": 42}

    def test_parse_json_response_with_extra_text(self):
        """Test parsing JSON response with extra text."""
        agent = OllamaAgent("TestAgent", "testing")
        response = 'Here is the JSON: {"key": "value"} End of response.'

        result = agent._parse_json_response(response)

        assert result == {"key": "value"}

    def test_parse_json_response_invalid(self):
        """Test parsing invalid JSON response."""
        agent = OllamaAgent("TestAgent", "testing")
        invalid_json = '{"key": "incomplete",}'

        with patch.object(agent, '_find_and_fix_json') as mock_fix:
            mock_fix.return_value = {"fixed": "json"}
            result = agent._parse_json_response(invalid_json)
            mock_fix.assert_called_once()

    def test_fix_incomplete_json_missing_quote(self):
        """Test fixing JSON with missing quote."""
        agent = OllamaAgent("TestAgent", "testing")
        incomplete = '{"key": "value'

        result = agent._fix_incomplete_json(incomplete)
        assert isinstance(result, dict)
        assert "key" in result

    def test_create_partial_response(self):
        """Test creating partial response from incomplete JSON."""
        agent = OllamaAgent("TestAgent", "testing")
        partial = '{"confidence": 0.8, "key":'

        with patch('re.search') as mock_search:
            mock_search.return_value = Mock()
            mock_search.return_value.group.return_value = "0.8"
            result = agent._create_partial_response(partial)
            assert isinstance(result, dict)
            assert "parsing_status" in result

    def test_get_fallback_response(self):
        """Test fallback response generation."""
        agent = OllamaAgent("TestAgent", "testing")
        result = agent._get_fallback_response()

        assert isinstance(result, dict)
        assert "error" in result
        assert result["confidence"] == 0.0


class TestSessionManagement:
    """Test cases for session management functions."""

    def test_get_shared_session_creates_new(self):
        """Test that get_shared_session creates a new session."""
        reset_shared_session()
        session = get_shared_session()
        assert session is not None

    def test_get_shared_session_reuses_existing(self):
        """Test that get_shared_session reuses existing session."""
        reset_shared_session()
        session1 = get_shared_session()
        session2 = get_shared_session()
        assert session1 is session2

    def test_reset_shared_session(self):
        """Test session reset functionality."""
        session1 = get_shared_session()
        reset_shared_session()
        session2 = get_shared_session()
        assert session1 is not session2
