from unittest.mock import AsyncMock, patch

import pytest

from agrotech_ai.websocket_handler import WebSocketHandler


class TestWebSocketHandler:
    """Integration tests for WebSocket handler."""

    @pytest.fixture
    def handler(self):
        """WebSocket handler fixture."""
        return WebSocketHandler()

    @pytest.fixture
    def mock_websocket(self):
        """Mock WebSocket fixture."""
        websocket = AsyncMock()
        websocket.accept = AsyncMock()
        websocket.send_json = AsyncMock()
        websocket.receive_json = AsyncMock()
        websocket.client.host = "127.0.0.1"
        return websocket

    @pytest.mark.asyncio
    @patch("agrotech_ai.websocket_handler.check_ollama_connection")
    async def test_handle_connection_ollama_not_running(
        self, mock_check, handler, mock_websocket
    ):
        """Test WebSocket connection when Ollama is not running."""
        mock_check.return_value = False

        await handler.handle_connection(mock_websocket)

        mock_websocket.accept.assert_called_once()
        mock_websocket.send_json.assert_called_once()

        call_args = mock_websocket.send_json.call_args[0][0]
        assert call_args["type"] == "error"
        assert "Ollama" in call_args["message"]

    @pytest.mark.asyncio
    @patch("agrotech_ai.websocket_handler.check_ollama_connection")
    async def test_handle_connection_success(self, mock_check, handler, mock_websocket):
        """Test successful WebSocket connection."""
        mock_check.return_value = True
        mock_websocket.receive_json.side_effect = Exception("Connection closed")

        with pytest.raises(Exception):
            await handler.handle_connection(mock_websocket)

        mock_websocket.accept.assert_called_once()

    @pytest.mark.asyncio
    async def test_process_message_ping(self, handler, mock_websocket):
        """Test processing ping message."""
        message = {"type": "ping"}

        await handler.process_message(mock_websocket, message)

        mock_websocket.send_json.assert_called_once()
        call_args = mock_websocket.send_json.call_args[0][0]
        assert call_args["type"] == "pong"
        assert call_args["message"] == "connection success"

    @pytest.mark.asyncio
    async def test_process_message_unknown_type(self, handler, mock_websocket):
        """Test processing unknown message type."""
        message = {"type": "unknown_type"}

        await handler.process_message(mock_websocket, message)

        mock_websocket.send_json.assert_called_once()
        call_args = mock_websocket.send_json.call_args[0][0]
        assert call_args["type"] == "error"

    @pytest.mark.asyncio
    async def test_handle_custom_scenario_missing_data(self, handler, mock_websocket):
        """Test custom scenario with missing required data."""
        message = {
            "type": "custom_scenario",
            "image_description": "Plants with leaves",
            # Missing environment_description
        }

        await handler.handle_custom_scenario(mock_websocket, message)

        mock_websocket.send_json.assert_called_once()
        call_args = mock_websocket.send_json.call_args[0][0]
        assert call_args["type"] == "error"

    @pytest.mark.asyncio
    async def test_handle_image_analysis_missing_image(self, handler, mock_websocket):
        """Test image analysis with missing image data."""
        message = {
            "type": "image_analysis",
            "environment_description": "Good conditions",
            # Missing image_data
        }

        await handler.handle_image_analysis(mock_websocket, message)

        mock_websocket.send_json.assert_called_once()
        call_args = mock_websocket.send_json.call_args[0][0]
        assert call_args["type"] == "error"

    @pytest.mark.asyncio
    @patch("agrotech_ai.websocket_handler.asyncio.sleep", new_callable=AsyncMock)
    async def test_analyze_scenario_complete_flow(
        self, mock_sleep, handler, mock_websocket
    ):
        """Test complete scenario analysis flow."""
        # Mock agent responses
        vision_result = {"crop_health": "healthy", "confidence": 0.9}
        soil_result = {"soil_moisture": 70, "confidence": 0.85}
        final_decision = {"overall_status": "good", "confidence": 0.88}

        with (
            patch.object(
                handler.agri_vision, "analyze_image", return_value=vision_result
            ),
            patch.object(
                handler.soil_sense, "analyze_environment", return_value=soil_result
            ),
            patch.object(
                handler.crop_master, "make_decision", return_value=final_decision
            ),
        ):

            await handler.analyze_scenario(
                mock_websocket,
                "Healthy plants",
                "Good soil conditions",
                "Test Scenario",
            )

            # Verify multiple send_json calls were made
            assert mock_websocket.send_json.call_count >= 5

            # Check that final status message was sent
            final_call = mock_websocket.send_json.call_args_list[-1][0][0]
            assert final_call["type"] == "status"
            assert "completado" in final_call["message"]

    @pytest.mark.asyncio
    @patch("agrotech_ai.websocket_handler.asyncio.sleep", new_callable=AsyncMock)
    async def test_analyze_image_scenario_complete_flow(
        self, mock_sleep, handler, mock_websocket, sample_base64_image
    ):
        """Test complete image analysis scenario flow."""
        # Mock agent responses
        image_analysis = {
            "image_description": "Healthy tomato plants",
            "soil_visual_indicators": "Dark soil",
            "environmental_context": "Good lighting",
            "plant_health_indicators": "Green leaves",
            "recommended_focus_areas": ["leaves", "soil"],
            "confidence": 0.92,
        }

        vision_result = {"crop_health": "healthy", "confidence": 0.9}

        soil_result = {"soil_moisture": 70, "confidence": 0.85}

        final_decision = {"overall_status": "good", "confidence": 0.88}

        with (
            patch.object(
                handler.image_vision, "analyze_image", return_value=image_analysis
            ),
            patch.object(
                handler.agri_vision, "analyze_image", return_value=vision_result
            ),
            patch.object(
                handler.soil_sense, "analyze_environment", return_value=soil_result
            ),
            patch.object(
                handler.crop_master, "make_decision", return_value=final_decision
            ),
        ):

            await handler.analyze_image_scenario(
                mock_websocket,
                sample_base64_image,
                "Good environmental conditions",
                "Image Analysis Test",
            )

            # Verify multiple send_json calls were made
            assert mock_websocket.send_json.call_count >= 6

            # Verify ImageVision was called
            handler.image_vision.analyze_image.assert_called_once_with(
                sample_base64_image
            )

    @pytest.mark.asyncio
    async def test_analyze_scenario_agent_error(self, handler, mock_websocket):
        """Test scenario analysis with agent error."""
        with patch.object(
            handler.agri_vision, "analyze_image", side_effect=Exception("Agent error")
        ):

            await handler.analyze_scenario(
                mock_websocket, "Test image", "Test environment", "Error Scenario"
            )

            # Should send error message
            error_calls = [
                call
                for call in mock_websocket.send_json.call_args_list
                if call[0][0].get("type") == "error"
            ]
            assert len(error_calls) > 0
