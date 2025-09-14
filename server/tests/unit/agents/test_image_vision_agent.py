import pytest
from unittest.mock import Mock, patch, AsyncMock
import base64
import io
from PIL import Image
from agents import ImageVisionAgent


class TestImageVisionAgent:
    """Test cases for ImageVision agent."""

    @pytest.fixture
    def agent(self):
        """ImageVision agent fixture."""
        return ImageVisionAgent()

    def test_agent_initialization(self, agent):
        """Test ImageVision agent initialization."""
        assert agent.role == "ImageVision"
        assert agent.expertise == "análisis visual de imágenes agrícolas"

    def test_optimize_image_resize(self, agent, sample_base64_image):
        """Test image optimization with resizing."""
        # Create a larger test image
        large_image = Image.new('RGB', (2048, 1536), color='green')
        buffer = io.BytesIO()
        large_image.save(buffer, format='JPEG')
        large_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

        optimized = agent._optimize_image(large_base64)

        # Should return optimized base64 string
        assert isinstance(optimized, str)
        assert len(optimized) < len(large_base64)

    def test_optimize_image_no_resize_needed(self, agent, sample_base64_image):
        """Test image optimization when no resize needed."""
        optimized = agent._optimize_image(sample_base64_image)

        # Should return optimized string
        assert isinstance(optimized, str)

    def test_optimize_image_error_handling(self, agent):
        """Test image optimization error handling."""
        invalid_base64 = "invalid_base64_data"

        # Should return original data on error
        result = agent._optimize_image(invalid_base64)
        assert result == invalid_base64

    @pytest.mark.asyncio
    async def test_analyze_image_success(self, agent, sample_base64_image):
        """Test successful image analysis."""
        mock_response = {
            "response": """{
                "image_description": "Healthy tomato plants",
                "soil_visual_indicators": "Dark soil",
                "environmental_context": "Good lighting",
                "plant_health_indicators": "Green leaves",
                "recommended_focus_areas": ["leaves", "soil"],
                "confidence": 0.9
            }"""
        }

        with patch.object(agent.session, 'post') as mock_post:
            mock_post.return_value = Mock()
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = mock_response

            result = await agent.analyze_image(sample_base64_image)

            assert isinstance(result, dict)
            assert "image_description" in result
            assert result["confidence"] == 0.9

    @pytest.mark.asyncio
    async def test_analyze_image_non_agricultural(self, agent, sample_base64_image):
        """Test image analysis with non-agricultural image."""
        mock_response = {
            "response": """{
                "is_agricultural_image": false,
                "reason": "La imagen no contiene elementos agrícolas",
                "confidence": 0.98,
                "image_description": null,
                "soil_visual_indicators": null,
                "environmental_context": null,
                "plant_health_indicators": null,
                "recommended_focus_areas": null
            }"""
        }

        with patch.object(agent.session, 'post') as mock_post:
            mock_post.return_value = Mock()
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = mock_response

            result = await agent.analyze_image(sample_base64_image)

            assert isinstance(result, dict)
            assert result.get("is_agricultural_image") == False

    @pytest.mark.asyncio
    async def test_analyze_image_timeout(self, agent, sample_base64_image):
        """Test image analysis with timeout."""
        with patch.object(agent.session, 'post') as mock_post:
            mock_post.side_effect = Exception("timeout")

            result = await agent.analyze_image(sample_base64_image)

            # Should return fallback response
            assert isinstance(result, dict)
            assert result["confidence"] == 0.0

    @pytest.mark.asyncio
    async def test_analyze_image_invalid_response(self, agent, sample_base64_image):
        """Test image analysis with invalid JSON response."""
        mock_response = {"response": "Invalid JSON response"}

        with patch.object(agent.session, 'post') as mock_post:
            mock_post.return_value = Mock()
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = mock_response

            result = await agent.analyze_image(sample_base64_image)

            # Should handle parsing error gracefully
            assert isinstance(result, dict)

    def test_get_fallback_response(self, agent):
        """Test fallback response generation."""
        result = agent._get_fallback_response()

        expected_keys = [
            "image_description",
            "soil_visual_indicators",
            "environmental_context",
            "plant_health_indicators",
            "recommended_focus_areas",
            "confidence"
        ]

        for key in expected_keys:
            assert key in result

        assert result["confidence"] == 0.0
        assert "Error en análisis" in result["image_description"]
