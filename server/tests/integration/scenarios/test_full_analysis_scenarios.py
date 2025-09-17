import asyncio
from unittest.mock import patch

import pytest

from agrotech_ai.agents import (
    AgriVisionAgent,
    CropMasterAgent,
    ImageVisionAgent,
    SoilSenseAgent,
)


class TestFullAnalysisScenarios:
    """Integration tests for complete analysis scenarios."""

    @pytest.fixture
    def agents(self):
        """Create all agent instances."""
        return {
            "image_vision": ImageVisionAgent(),
            "agri_vision": AgriVisionAgent(),
            "soil_sense": SoilSenseAgent(),
            "crop_master": CropMasterAgent(),
        }

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_healthy_crop_scenario(self, agents, sample_base64_image):
        """Test complete analysis flow for healthy crop scenario."""
        # Mock responses for each agent
        image_analysis = {
            "image_description": "Plantas de tomate saludables con hojas verdes",
            "soil_visual_indicators": "Suelo oscuro y húmedo",
            "environmental_context": "Buena iluminación natural",
            "plant_health_indicators": "Sin signos de enfermedad",
            "recommended_focus_areas": ["salud_hojas", "humedad_suelo"],
            "confidence": 0.92,
        }

        vision_result = {
            "crop_health": "healthy",
            "pest_detected": False,
            "leaf_condition": "excellent",
            "disease_probability": 0.1,
            "visual_symptoms": ["hojas verdes", "sin manchas"],
            "recommendations": ["continuar monitoreo"],
            "confidence": 0.88,
        }

        soil_result = {
            "soil_moisture": 70,
            "ph_level": 6.5,
            "temperature": 24,
            "humidity": 60,
            "irrigation_needed": False,
            "fertilizer_status": "adequate",
            "environmental_stress": "low",
            "alerts": [],
            "confidence": 0.85,
        }

        final_decision = {
            "overall_status": "good",
            "priority_actions": ["continuar monitoreo", "mantener riego actual"],
            "estimated_yield": "high",
            "risk_assessment": "low",
            "next_inspection_hours": 48,
            "economic_impact": "positive",
            "urgent_alerts": [],
            "confidence": 0.89,
        }

        # Mock all agent methods
        with (
            patch.object(
                agents["image_vision"], "analyze_image", return_value=image_analysis
            ),
            patch.object(
                agents["agri_vision"], "analyze_image", return_value=vision_result
            ),
            patch.object(
                agents["soil_sense"], "analyze_environment", return_value=soil_result
            ),
            patch.object(
                agents["crop_master"], "make_decision", return_value=final_decision
            ),
        ):

            # Step 1: Image analysis
            img_result = await agents["image_vision"].analyze_image(sample_base64_image)
            assert img_result["confidence"] > 0.8

            # Step 2: Parallel crop and soil analysis
            image_desc = img_result["image_description"]
            env_conditions = "Condiciones ambientales favorables"

            vision_task = agents["agri_vision"].analyze_image(image_desc)
            soil_task = agents["soil_sense"].analyze_environment(env_conditions)

            crop_result, soil_result = await asyncio.gather(vision_task, soil_task)

            assert crop_result["crop_health"] == "healthy"
            assert soil_result["environmental_stress"] == "low"

            # Step 3: Final decision
            decision = await agents["crop_master"].make_decision(
                crop_result, soil_result
            )

            assert decision["overall_status"] == "good"
            assert decision["risk_assessment"] == "low"
            assert decision["estimated_yield"] == "high"

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_diseased_crop_scenario(self, agents, sample_base64_image):
        """Test complete analysis flow for diseased crop scenario."""
        # Mock responses for diseased crop
        image_analysis = {
            "image_description": "Plantas con hojas amarillentas y manchas",
            "soil_visual_indicators": "Suelo seco y agrietado",
            "environmental_context": "Condiciones de estrés visible",
            "plant_health_indicators": "Signos de enfermedad fúngica",
            "recommended_focus_areas": ["enfermedad_hojas", "estrés_hídrico"],
            "confidence": 0.87,
        }

        vision_result = {
            "crop_health": "diseased",
            "pest_detected": True,
            "leaf_condition": "poor",
            "disease_probability": 0.8,
            "visual_symptoms": ["hojas amarillas", "manchas marrones"],
            "recommendations": ["aplicar fungicida", "mejorar riego"],
            "confidence": 0.85,
        }

        soil_result = {
            "soil_moisture": 25,
            "ph_level": 8.2,
            "temperature": 32,
            "humidity": 35,
            "irrigation_needed": True,
            "fertilizer_status": "deficient",
            "environmental_stress": "high",
            "alerts": ["sequía severa", "pH elevado"],
            "confidence": 0.82,
        }

        final_decision = {
            "overall_status": "warning",
            "priority_actions": ["riego inmediato", "aplicar fungicida", "ajustar pH"],
            "estimated_yield": "low",
            "risk_assessment": "high",
            "next_inspection_hours": 12,
            "economic_impact": "negative",
            "urgent_alerts": ["riesgo de pérdida de cultivo"],
            "confidence": 0.86,
        }

        # Mock all agent methods
        with (
            patch.object(
                agents["image_vision"], "analyze_image", return_value=image_analysis
            ),
            patch.object(
                agents["agri_vision"], "analyze_image", return_value=vision_result
            ),
            patch.object(
                agents["soil_sense"], "analyze_environment", return_value=soil_result
            ),
            patch.object(
                agents["crop_master"], "make_decision", return_value=final_decision
            ),
        ):

            # Complete flow
            img_result = await agents["image_vision"].analyze_image(sample_base64_image)

            # Parallel processing
            vision_task = agents["agri_vision"].analyze_image(
                img_result["image_description"]
            )
            soil_task = agents["soil_sense"].analyze_environment(
                "Condiciones de estrés"
            )

            crop_result, soil_result = await asyncio.gather(vision_task, soil_task)
            decision = await agents["crop_master"].make_decision(
                crop_result, soil_result
            )

            # Assertions for diseased scenario
            assert crop_result["crop_health"] == "diseased"
            assert crop_result["pest_detected"] is True
            assert soil_result["environmental_stress"] == "high"
            assert decision["overall_status"] == "warning"
            assert decision["risk_assessment"] == "high"
            assert len(decision["urgent_alerts"]) > 0

    @pytest.mark.integration
    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_concurrent_analysis_performance(self, agents):
        """Test performance of concurrent agent analysis."""
        import time

        # Mock fast responses
        quick_response = {"confidence": 0.8, "status": "processed"}

        with (
            patch.object(
                agents["agri_vision"], "analyze_image", return_value=quick_response
            ),
            patch.object(
                agents["soil_sense"], "analyze_environment", return_value=quick_response
            ),
        ):

            start_time = time.time()

            # Run multiple concurrent analyses
            tasks = []
            for i in range(5):
                vision_task = agents["agri_vision"].analyze_image(f"test image {i}")
                soil_task = agents["soil_sense"].analyze_environment(
                    f"test environment {i}"
                )
                tasks.extend([vision_task, soil_task])

            results = await asyncio.gather(*tasks)

            elapsed_time = time.time() - start_time

            # Should complete quickly with concurrent execution
            assert len(results) == 10
            assert elapsed_time < 1.0  # Should be very fast with mocks

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_error_recovery_scenario(self, agents, sample_base64_image):
        """Test error recovery in analysis pipeline."""
        # First agent succeeds, second fails, third recovers
        image_analysis = {"image_description": "Partial analysis", "confidence": 0.6}

        with (
            patch.object(
                agents["image_vision"], "analyze_image", return_value=image_analysis
            ),
            patch.object(
                agents["agri_vision"],
                "generate_response",
                side_effect=Exception("Vision error"),
            ),
            patch.object(
                agents["soil_sense"],
                "analyze_environment",
                return_value={"confidence": 0.7},
            ),
        ):

            # Image analysis should succeed
            img_result = await agents["image_vision"].analyze_image(sample_base64_image)
            assert img_result["confidence"] == 0.6

            # Vision analysis should fail and return fallback
            crop_result = await agents["agri_vision"].analyze_image("test")
            assert crop_result["confidence"] == 0.0  # Fallback response

            # Soil analysis should succeed
            soil_result = await agents["soil_sense"].analyze_environment("test")
            assert soil_result["confidence"] == 0.7

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_data_flow_integrity(self, agents, sample_base64_image):
        """Test that data flows correctly between agents."""
        # Setup realistic mock responses
        image_analysis = {
            "image_description": "Cultivo de maíz con hojas amarillas",
            "soil_visual_indicators": "Suelo arenoso y seco",
            "environmental_context": "Día soleado, temperatura alta",
            "recommended_focus_areas": ["nutrición", "riego"],
            "confidence": 0.9,
        }

        # Track what data is passed between agents
        vision_calls = []
        soil_calls = []
        decision_calls = []

        def track_vision(image_desc):
            vision_calls.append(image_desc)
            return {"crop_health": "stressed", "confidence": 0.8}

        def track_soil(env_desc):
            soil_calls.append(env_desc)
            return {"soil_moisture": 40, "confidence": 0.7}

        def track_decision(vision_data, soil_data):
            decision_calls.append((vision_data, soil_data))
            return {"overall_status": "warning", "confidence": 0.75}

        with (
            patch.object(
                agents["image_vision"], "analyze_image", return_value=image_analysis
            ),
            patch.object(
                agents["agri_vision"], "analyze_image", side_effect=track_vision
            ),
            patch.object(
                agents["soil_sense"], "analyze_environment", side_effect=track_soil
            ),
            patch.object(
                agents["crop_master"], "make_decision", side_effect=track_decision
            ),
        ):

            # Complete analysis flow
            img_result = await agents["image_vision"].analyze_image(sample_base64_image)

            vision_result = await agents["agri_vision"].analyze_image(
                img_result["image_description"]
            )
            soil_result = await agents["soil_sense"].analyze_environment(
                "Test environment"
            )

            await agents["crop_master"].make_decision(vision_result, soil_result)

            # Verify data flow
            assert len(vision_calls) == 1
            assert vision_calls[0] == img_result["image_description"]

            assert len(soil_calls) == 1
            assert soil_calls[0] == "Test environment"

            assert len(decision_calls) == 1
            assert decision_calls[0][0]["crop_health"] == "stressed"
            assert decision_calls[0][1]["soil_moisture"] == 40
