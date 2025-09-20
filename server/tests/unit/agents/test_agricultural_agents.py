from unittest.mock import Mock, patch

import pytest

from agrotech_ai.agents import AgriVisionAgent, CropMasterAgent, SoilSenseAgent


class TestAgriVisionAgent:
    """Test cases for AgriVision agent."""

    @pytest.fixture
    def agent(self):
        """AgriVision agent fixture."""
        return AgriVisionAgent()

    def test_agent_initialization(self, agent):
        """Test AgriVision agent initialization."""
        assert agent.role == "AgriVision"
        assert agent.expertise == "análisis visual de cultivos"

    @pytest.mark.asyncio
    async def test_analyze_image_healthy_crop(self, agent):
        """Test image analysis for healthy crop."""
        mock_response = {
            "response": """{
                "crop_health": "healthy",
                "pest_detected": false,
                "leaf_condition": "excellent",
                "disease_probability": 0.1,
                "visual_symptoms": ["hojas verdes", "sin manchas"],
                "recommendations": ["continuar monitoreo"],
                "confidence": 0.9
            }"""
        }

        with patch.object(agent.session, "post") as mock_post:
            mock_post.return_value = Mock()
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = mock_response

            result = await agent.analyze_image(
                "Healthy tomato plants with green leaves"
            )

            assert result["crop_health"] == "healthy"
            assert result["pest_detected"] is False
            assert result["leaf_condition"] == "excellent"
            assert result["confidence"] == 0.9

    @pytest.mark.asyncio
    async def test_analyze_image_diseased_crop(self, agent):
        """Test image analysis for diseased crop."""
        mock_response = {
            "response": """{
                "crop_health": "diseased",
                "pest_detected": true,
                "leaf_condition": "poor",
                "disease_probability": 0.8,
                "visual_symptoms": ["manchas amarillas", "hojas marchitas"],
                "recommendations": ["aplicar fungicida", "mejorar ventilación"],
                "confidence": 0.85
            }"""
        }

        with patch.object(agent.session, "post") as mock_post:
            mock_post.return_value = Mock()
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = mock_response

            result = await agent.analyze_image("Plants with yellowing leaves and spots")

            assert result["crop_health"] == "diseased"
            assert result["pest_detected"] is True
            assert result["leaf_condition"] == "poor"
            assert result["disease_probability"] == 0.8

    def test_get_fallback_response(self, agent):
        """Test fallback response for AgriVision."""
        result = agent._get_fallback_response()

        expected_keys = [
            "crop_health",
            "pest_detected",
            "leaf_condition",
            "disease_probability",
            "visual_symptoms",
            "recommendations",
            "confidence",
        ]

        for key in expected_keys:
            assert key in result

        assert result["crop_health"] == "unknown"
        assert result["confidence"] == 0.0


class TestSoilSenseAgent:
    """Test cases for SoilSense agent."""

    @pytest.fixture
    def agent(self):
        """SoilSense agent fixture."""
        return SoilSenseAgent()

    def test_agent_initialization(self, agent):
        """Test SoilSense agent initialization."""
        assert agent.role == "SoilSense"
        assert agent.expertise == "condiciones ambientales y del suelo"

    @pytest.mark.asyncio
    async def test_analyze_environment_good_conditions(self, agent):
        """Test environmental analysis with good conditions."""
        mock_response = {
            "response": """{
                "soil_moisture": 70,
                "ph_level": 6.5,
                "temperature": 24,
                "humidity": 60,
                "irrigation_needed": false,
                "fertilizer_status": "adequate",
                "environmental_stress": "low",
                "alerts": [],
                "confidence": 0.9
            }"""
        }

        with patch.object(agent.session, "post") as mock_post:
            mock_post.return_value = Mock()
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = mock_response

            conditions = "Good soil moisture, optimal pH, moderate temperature"
            result = await agent.analyze_environment(conditions)

            assert result["soil_moisture"] == 70
            assert result["ph_level"] == 6.5
            assert result["irrigation_needed"] is False
            assert result["environmental_stress"] == "low"

    @pytest.mark.asyncio
    async def test_analyze_environment_stress_conditions(self, agent):
        """Test environmental analysis with stress conditions."""
        mock_response = {
            "response": """{
                "soil_moisture": 25,
                "ph_level": 8.2,
                "temperature": 35,
                "humidity": 30,
                "irrigation_needed": true,
                "fertilizer_status": "deficient",
                "environmental_stress": "high",
                "alerts": ["humedad muy baja", "pH alto", "estrés térmico"],
                "confidence": 0.85
            }"""
        }

        with patch.object(agent.session, "post") as mock_post:
            mock_post.return_value = Mock()
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = mock_response

            conditions = "Dry soil, high pH, hot temperature, low humidity"
            result = await agent.analyze_environment(conditions)

            assert result["soil_moisture"] == 25
            assert result["ph_level"] == 8.2
            assert result["irrigation_needed"] is True
            assert result["environmental_stress"] == "high"
            assert len(result["alerts"]) == 3

    def test_get_fallback_response(self, agent):
        """Test fallback response for SoilSense."""
        result = agent._get_fallback_response()

        expected_keys = [
            "soil_moisture",
            "ph_level",
            "temperature",
            "humidity",
            "irrigation_needed",
            "fertilizer_status",
            "environmental_stress",
            "alerts",
            "confidence",
        ]

        for key in expected_keys:
            assert key in result

        assert result["soil_moisture"] == 50
        assert result["confidence"] == 0.0


class TestCropMasterAgent:
    """Test cases for CropMaster agent."""

    @pytest.fixture
    def agent(self):
        """CropMaster agent fixture."""
        return CropMasterAgent()

    def test_agent_initialization(self, agent):
        """Test CropMaster agent initialization."""
        assert agent.role == "CropMaster"
        assert agent.expertise == "toma de decisiones agrícolas integrales"

    @pytest.mark.asyncio
    async def test_make_decision_healthy_scenario(
        self, agent, sample_vision_result, sample_soil_result
    ):
        """Test decision making for healthy scenario."""
        mock_response = {
            "response": """{
                "overall_status": "good",
                "priority_actions": ["continuar monitoreo", "mantener riego actual"],
                "estimated_yield": "high",
                "risk_assessment": "low",
                "next_inspection_hours": 48,
                "economic_impact": "positive",
                "urgent_alerts": [],
                "confidence": 0.92
            }"""
        }

        with patch.object(agent.session, "post") as mock_post:
            mock_post.return_value = Mock()
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = mock_response

            result = await agent.make_decision(sample_vision_result, sample_soil_result)

            assert result["overall_status"] == "good"
            assert result["estimated_yield"] == "high"
            assert result["risk_assessment"] == "low"
            assert result["economic_impact"] == "positive"
            assert len(result["urgent_alerts"]) == 0

    @pytest.mark.asyncio
    async def test_make_decision_critical_scenario(self, agent):
        """Test decision making for critical scenario."""
        vision_data = {
            "crop_health": "diseased",
            "pest_detected": True,
            "leaf_condition": "poor",
            "disease_probability": 0.9,
            "confidence": 0.85,
        }

        soil_data = {
            "soil_moisture": 20,
            "irrigation_needed": True,
            "environmental_stress": "high",
            "alerts": ["sequía severa"],
            "confidence": 0.8,
        }

        mock_response = {
            "response": """{
                "overall_status": "critical",
                "priority_actions": [
                    "riego inmediato",
                    "aplicar pesticida",
                    "consultar especialista"
                ],
                "estimated_yield": "low",
                "risk_assessment": "critical",
                "next_inspection_hours": 6,
                "economic_impact": "negative",
                "urgent_alerts": ["pérdida de cultivo inminente"],
                "confidence": 0.88
            }"""
        }

        with patch.object(agent.session, "post") as mock_post:
            mock_post.return_value = Mock()
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = mock_response

            result = await agent.make_decision(vision_data, soil_data)

            assert result["overall_status"] == "critical"
            assert result["estimated_yield"] == "low"
            assert result["risk_assessment"] == "critical"
            assert result["economic_impact"] == "negative"
            assert len(result["urgent_alerts"]) > 0

    @pytest.mark.asyncio
    async def test_make_decision_with_empty_data(self, agent):
        """Test decision making with empty or invalid data."""
        vision_data = {}
        soil_data = {}

        with patch.object(agent.session, "post") as mock_post:
            mock_post.side_effect = Exception("Connection error")

            result = await agent.make_decision(vision_data, soil_data)

            # Should return fallback response
            assert result["overall_status"] == "unknown"
            assert result["confidence"] == 0.0

    def test_get_fallback_response(self, agent):
        """Test fallback response for CropMaster."""
        result = agent._get_fallback_response()

        expected_keys = [
            "overall_status",
            "priority_actions",
            "estimated_yield",
            "risk_assessment",
            "next_inspection_hours",
            "economic_impact",
            "urgent_alerts",
            "confidence",
        ]

        for key in expected_keys:
            assert key in result

        assert result["overall_status"] == "unknown"
        assert result["confidence"] == 0.0
        assert isinstance(result["priority_actions"], list)
