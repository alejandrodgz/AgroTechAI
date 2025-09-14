import pytest
from unittest.mock import Mock, patch, MagicMock
import json
from ollama_client import (
    OllamaAgent,
    get_shared_session,
    reset_shared_session,
    check_ollama_connection
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


class TestOllamaConnection:
    """Test cases for Ollama connection checking."""

    @patch('ollama_client.requests.get')
    def test_check_ollama_connection_success(self, mock_get):
        """Test successful Ollama connection check."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        result = check_ollama_connection()

        assert result is True
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert "/api/tags" in call_args[0][0]
        assert call_args[1]["timeout"] == 5

    @patch('ollama_client.requests.get')
    def test_check_ollama_connection_failure(self, mock_get):
        """Test failed Ollama connection check."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        result = check_ollama_connection()

        assert result is False
        mock_get.assert_called_once()

    @patch('ollama_client.requests.get')
    def test_check_ollama_connection_timeout(self, mock_get):
        """Test Ollama connection check with timeout."""
        import requests
        mock_get.side_effect = requests.exceptions.Timeout("Connection timeout")

        result = check_ollama_connection()

        assert result is False
        mock_get.assert_called_once()

    @patch('ollama_client.requests.get')
    def test_check_ollama_connection_connection_error(self, mock_get):
        """Test Ollama connection check with connection error."""
        import requests
        mock_get.side_effect = requests.exceptions.ConnectionError("Connection refused")

        result = check_ollama_connection()

        assert result is False
        mock_get.assert_called_once()

    @patch('ollama_client.requests.get')
    def test_check_ollama_connection_generic_request_error(self, mock_get):
        """Test Ollama connection check with generic request error."""
        import requests
        mock_get.side_effect = requests.exceptions.RequestException("Generic error")

        result = check_ollama_connection()

        assert result is False
        mock_get.assert_called_once()


class TestFindAndFixJson:
    """Test cases for _find_and_fix_json method."""

    def test_find_and_fix_json_with_valid_object(self):
        """Test _find_and_fix_json with valid JSON object."""
        agent = OllamaAgent("TestAgent", "testing")
        text_blob = 'Some text before {"key": "value", "number": 42}'

        result = agent._find_and_fix_json(text_blob)

        assert isinstance(result, dict)
        assert result.get("key") == "value"
        assert result.get("number") == 42

    def test_find_and_fix_json_with_valid_array(self):
        """Test _find_and_fix_json with valid JSON array."""
        agent = OllamaAgent("TestAgent", "testing")
        text_blob = 'Some text before ["item1", "item2", "item3"]'

        result = agent._find_and_fix_json(text_blob)

        assert isinstance(result, list)
        assert len(result) == 3
        assert "item1" in result

    def test_find_and_fix_json_prefers_first_object(self):
        """Test that _find_and_fix_json prefers the first JSON structure found."""
        agent = OllamaAgent("TestAgent", "testing")
        text_blob = '{"old": "data"} some text {"new": "data"}'

        result = agent._find_and_fix_json(text_blob)

        assert isinstance(result, dict)
        assert result.get("old") == "data"
        assert "new" not in result

    def test_find_and_fix_json_prefers_first_structure(self):
        """Test that _find_and_fix_json prefers the first JSON structure found."""
        agent = OllamaAgent("TestAgent", "testing")
        text_blob = 'text ["array", "items"] then {"key": "value"}'

        result = agent._find_and_fix_json(text_blob)

        # Should extract the array since it appears first
        assert isinstance(result, list)
        assert len(result) == 2
        assert "array" in result

    def test_find_and_fix_json_prefers_object_when_first(self):
        """Test that _find_and_fix_json prefers object when object appears before array."""
        agent = OllamaAgent("TestAgent", "testing")
        text_blob = 'text {"key": "value"} then ["item1", "item2"]'

        result = agent._find_and_fix_json(text_blob)

        # Should extract the object since it appears first
        assert isinstance(result, dict)
        assert result.get("key") == "value"

    def test_find_and_fix_json_with_incomplete_object(self):
        """Test _find_and_fix_json with incomplete JSON object."""
        agent = OllamaAgent("TestAgent", "testing")
        text_blob = 'Some text {"key": "value", "incomplete'

        with patch.object(agent, '_fix_incomplete_json') as mock_fix:
            mock_fix.return_value = {"key": "value", "fixed": True}
            result = agent._find_and_fix_json(text_blob)

            mock_fix.assert_called_once_with('{"key": "value", "incomplete')
            assert result == {"key": "value", "fixed": True}

    def test_find_and_fix_json_with_incomplete_array(self):
        """Test _find_and_fix_json with incomplete JSON array."""
        agent = OllamaAgent("TestAgent", "testing")
        text_blob = 'Some text ["item1", "item2"'

        with patch.object(agent, '_fix_incomplete_json') as mock_fix:
            mock_fix.return_value = ["item1", "item2"]
            result = agent._find_and_fix_json(text_blob)

            mock_fix.assert_called_once_with('["item1", "item2"')
            assert result == ["item1", "item2"]

    def test_find_and_fix_json_no_json_found(self):
        """Test _find_and_fix_json when no JSON structure is found."""
        agent = OllamaAgent("TestAgent", "testing")
        text_blob = 'Just some plain text without any JSON structures'

        with patch.object(agent, '_create_partial_response') as mock_partial:
            mock_partial.return_value = {"error": "no JSON found"}
            result = agent._find_and_fix_json(text_blob)

            mock_partial.assert_called_once_with(text_blob)
            assert result == {"error": "no JSON found"}

    def test_find_and_fix_json_empty_text(self):
        """Test _find_and_fix_json with empty text."""
        agent = OllamaAgent("TestAgent", "testing")
        text_blob = ''

        with patch.object(agent, '_create_partial_response') as mock_partial:
            mock_partial.return_value = {"error": "empty text"}
            result = agent._find_and_fix_json(text_blob)

            mock_partial.assert_called_once_with('')
            assert result == {"error": "empty text"}

    def test_find_and_fix_json_nested_structures(self):
        """Test _find_and_fix_json with properly formed nested JSON."""
        agent = OllamaAgent("TestAgent", "testing")
        text_blob = 'Text before {"outer": {"inner": "value"}, "simple": "data"}'

        result = agent._find_and_fix_json(text_blob)

        assert isinstance(result, dict)
        assert "outer" in result
        assert "simple" in result
        assert result["outer"]["inner"] == "value"
        assert result["simple"] == "data"

    def test_find_and_fix_json_multiple_same_type(self):
        """Test _find_and_fix_json with multiple objects, should pick the first one."""
        agent = OllamaAgent("TestAgent", "testing")
        text_blob = '{"first": 1} middle text {"second": 2} end text {"third": 3}'

        result = agent._find_and_fix_json(text_blob)

        assert isinstance(result, dict)
        assert result == {"first": 1}
