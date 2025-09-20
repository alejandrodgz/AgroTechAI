import asyncio
from unittest.mock import AsyncMock, Mock

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient

from agrotech_ai.agents import (
    AgriVisionAgent,
    CropMasterAgent,
    ImageVisionAgent,
    SoilSenseAgent,
)
from agrotech_ai.app import app
from agrotech_ai.ollama_client import reset_shared_session


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def test_client():
    """FastAPI test client fixture."""
    with TestClient(app) as client:
        yield client


@pytest.fixture
async def async_client():
    """Async HTTP client fixture."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture
def mock_ollama_response():
    """Mock Ollama API response."""
    return {
        "response": '{"test": "data", "confidence": 0.85}',
        "done": True,
        "created_at": "2024-01-01T00:00:00Z",
    }


@pytest.fixture
def mock_requests_session():
    """Mock requests session for testing."""
    session = Mock()
    session.post.return_value = Mock()
    session.post.return_value.status_code = 200
    session.post.return_value.json.return_value = {
        "response": '{"test": "response", "confidence": 0.9}'
    }
    return session


@pytest.fixture
def sample_base64_image():
    """Sample base64 encoded image data for testing."""
    # This is a minimal 1x1 PNG image in base64
    return (
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk"
        "+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
    )


@pytest.fixture
def image_vision_agent():
    """ImageVision agent fixture."""
    agent = ImageVisionAgent()
    agent.session = Mock()
    return agent


@pytest.fixture
def agri_vision_agent():
    """AgriVision agent fixture."""
    agent = AgriVisionAgent()
    agent.session = Mock()
    return agent


@pytest.fixture
def soil_sense_agent():
    """SoilSense agent fixture."""
    agent = SoilSenseAgent()
    agent.session = Mock()
    return agent


@pytest.fixture
def crop_master_agent():
    """CropMaster agent fixture."""
    agent = CropMasterAgent()
    agent.session = Mock()
    return agent


@pytest.fixture
def sample_image_analysis():
    """Sample image analysis result."""
    return {
        "image_description": "Healthy tomato plants with green leaves",
        "soil_visual_indicators": "Dark, moist soil visible",
        "environmental_context": "Good lighting, outdoor growth",
        "plant_health_indicators": "No visible disease signs",
        "recommended_focus_areas": ["leaf_health", "soil_moisture"],
        "confidence": 0.92,
    }


@pytest.fixture
def sample_vision_result():
    """Sample AgriVision analysis result."""
    return {
        "crop_health": "healthy",
        "pest_detected": False,
        "leaf_condition": "good",
        "disease_probability": 0.1,
        "visual_symptoms": ["green leaves", "no spots"],
        "recommendations": ["continue monitoring"],
        "confidence": 0.88,
    }


@pytest.fixture
def sample_soil_result():
    """Sample SoilSense analysis result."""
    return {
        "soil_moisture": 65,
        "ph_level": 6.8,
        "temperature": 24,
        "humidity": 55,
        "irrigation_needed": False,
        "fertilizer_status": "adequate",
        "environmental_stress": "low",
        "alerts": [],
        "confidence": 0.85,
    }


@pytest.fixture(autouse=True)
def reset_session():
    """Reset shared session before each test."""
    reset_shared_session()
    yield
    reset_shared_session()


@pytest.fixture
def mock_websocket():
    """Mock WebSocket connection."""
    websocket = AsyncMock()
    websocket.accept = AsyncMock()
    websocket.send_json = AsyncMock()
    websocket.receive_json = AsyncMock()
    websocket.client.host = "127.0.0.1"
    return websocket
