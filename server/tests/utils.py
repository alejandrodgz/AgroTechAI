"""
Test utilities and helpers for AgroTech AI tests.
"""

import base64
import io
import json
from PIL import Image
from typing import Dict, Any
from unittest.mock import Mock


def create_test_image(width: int = 100, height: int = 100, color: str = 'green') -> str:
    """Create a test image and return as base64 string."""
    image = Image.new('RGB', (width, height), color=color)
    buffer = io.BytesIO()
    image.save(buffer, format='JPEG')
    return base64.b64encode(buffer.getvalue()).decode('utf-8')


def create_mock_ollama_response(data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a mock Ollama API response."""
    return {
        "response": json.dumps(data),
        "done": True,
        "created_at": "2024-01-01T00:00:00Z"
    }


def mock_requests_session(response_data: Dict[str, Any], status_code: int = 200):
    """Create a mock requests session with predefined response."""
    session = Mock()
    session.post.return_value = Mock()
    session.post.return_value.status_code = status_code
    session.post.return_value.json.return_value = create_mock_ollama_response(response_data)
    return session


class MockWebSocket:
    """Mock WebSocket for testing."""

    def __init__(self):
        self.sent_messages = []
        self.received_messages = []
        self.client = Mock()
        self.client.host = "127.0.0.1"

    async def accept(self):
        """Mock accept method."""
        pass

    async def send_json(self, data):
        """Mock send_json method."""
        self.sent_messages.append(data)

    async def receive_json(self):
        """Mock receive_json method."""
        if self.received_messages:
            return self.received_messages.pop(0)
        raise Exception("No more messages")

    def add_message(self, message):
        """Add message to be received."""
        self.received_messages.append(message)


def get_sample_responses():
    """Get sample responses for different agents."""
    return {
        'image_vision': {
            "image_description": "Plantas de tomate saludables con hojas verdes brillantes",
            "soil_visual_indicators": "Suelo oscuro y bien húmedo",
            "environmental_context": "Condiciones de luz natural favorable",
            "plant_health_indicators": "Sin signos visibles de enfermedad o plagas",
            "recommended_focus_areas": ["salud_foliar", "humedad_suelo", "crecimiento"],
            "confidence": 0.92
        },
        'agri_vision': {
            "crop_health": "healthy",
            "pest_detected": False,
            "leaf_condition": "excellent",
            "disease_probability": 0.05,
            "visual_symptoms": ["hojas verdes", "crecimiento vigoroso"],
            "recommendations": ["continuar monitoreo regular", "mantener condiciones actuales"],
            "confidence": 0.88
        },
        'soil_sense': {
            "soil_moisture": 68,
            "ph_level": 6.7,
            "temperature": 23,
            "humidity": 58,
            "irrigation_needed": False,
            "fertilizer_status": "adequate",
            "environmental_stress": "low",
            "alerts": [],
            "confidence": 0.85
        },
        'crop_master': {
            "overall_status": "good",
            "priority_actions": ["continuar monitoreo", "revisar en 48 horas"],
            "estimated_yield": "high",
            "risk_assessment": "low",
            "next_inspection_hours": 48,
            "economic_impact": "positive",
            "urgent_alerts": [],
            "confidence": 0.89
        }
    }


def get_stress_scenario_responses():
    """Get sample responses for stress/disease scenario."""
    return {
        'image_vision': {
            "image_description": "Plantas con hojas amarillentas y algunas manchas oscuras",
            "soil_visual_indicators": "Suelo seco con grietas superficiales",
            "environmental_context": "Signos de estrés hídrico y posible deficiencia nutricional",
            "plant_health_indicators": "Clorosis en hojas inferiores, manchas necróticas",
            "recommended_focus_areas": ["estrés_hídrico", "deficiencia_nutricional", "patologías"],
            "confidence": 0.87
        },
        'agri_vision': {
            "crop_health": "stressed",
            "pest_detected": False,
            "leaf_condition": "poor",
            "disease_probability": 0.6,
            "visual_symptoms": ["amarillamiento", "manchas necróticas", "deshidratación"],
            "recommendations": ["aumentar riego", "análisis de suelo", "fertilización"],
            "confidence": 0.82
        },
        'soil_sense': {
            "soil_moisture": 30,
            "ph_level": 7.8,
            "temperature": 29,
            "humidity": 40,
            "irrigation_needed": True,
            "fertilizer_status": "deficient",
            "environmental_stress": "high",
            "alerts": ["déficit hídrico", "pH elevado", "deficiencia de nutrientes"],
            "confidence": 0.78
        },
        'crop_master': {
            "overall_status": "warning",
            "priority_actions": ["riego inmediato", "análisis de suelo", "ajuste de pH", "fertilización"],
            "estimated_yield": "medium",
            "risk_assessment": "medium",
            "next_inspection_hours": 24,
            "economic_impact": "neutral",
            "urgent_alerts": ["déficit hídrico crítico"],
            "confidence": 0.83
        }
    }


def assert_agent_response_structure(response: Dict[str, Any], agent_type: str):
    """Assert that agent response has the expected structure."""
    common_fields = ["confidence"]

    type_specific_fields = {
        'image_vision': [
            "image_description", "soil_visual_indicators",
            "environmental_context", "plant_health_indicators",
            "recommended_focus_areas"
        ],
        'agri_vision': [
            "crop_health", "pest_detected", "leaf_condition",
            "disease_probability", "visual_symptoms", "recommendations"
        ],
        'soil_sense': [
            "soil_moisture", "ph_level", "temperature", "humidity",
            "irrigation_needed", "fertilizer_status", "environmental_stress", "alerts"
        ],
        'crop_master': [
            "overall_status", "priority_actions", "estimated_yield",
            "risk_assessment", "next_inspection_hours", "economic_impact", "urgent_alerts"
        ]
    }

    expected_fields = common_fields + type_specific_fields.get(agent_type, [])

    for field in expected_fields:
        assert field in response, f"Missing field '{field}' in {agent_type} response"

    # Type validations
    assert isinstance(response["confidence"], (int, float)), "Confidence should be numeric"
    assert 0.0 <= response["confidence"] <= 1.0, "Confidence should be between 0 and 1"

    if agent_type == 'agri_vision':
        assert response["crop_health"] in ["healthy", "stressed", "diseased", "unknown"]
        assert isinstance(response["pest_detected"], bool)
        assert response["leaf_condition"] in ["excellent", "good", "fair", "poor", "unknown"]

    if agent_type == 'soil_sense':
        assert 0 <= response["soil_moisture"] <= 100, "Soil moisture should be 0-100%"
        assert 4.0 <= response["ph_level"] <= 9.0, "pH should be 4.0-9.0"
        assert isinstance(response["irrigation_needed"], bool)

    if agent_type == 'crop_master':
        assert response["overall_status"] in ["excellent", "good", "warning", "critical", "unknown"]
        assert response["risk_assessment"] in ["low", "medium", "high", "critical", "unknown"]
