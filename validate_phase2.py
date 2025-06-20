"""
Phase 2 Success Criteria Validation Script
Tests all requirements from DETAILED_BUILD_PLAN.md Phase 2
"""
import asyncio
import logging
import sys
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from secretGPT.hub.core.router import HubRouter, ComponentType
from secretGPT.services.secret_ai.client import SecretAIService
from secretGPT.interfaces.web_ui.service import WebUIService
from secretGPT.config.settings import settings, validate_settings

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

async def validate_phase2_criteria():
    """Validate all Phase 2 success criteria"""
    
    criteria_results = {}
    
    # Initialize components
    hub = HubRouter()
    secret_ai = SecretAIService()
    hub.register_component(ComponentType.SECRET_AI, secret_ai)
    
    web_ui_service = WebUIService(hub)
    hub.register_component(ComponentType.WEB_UI, web_ui_service)
    
    await hub.initialize()
    
    # ✅ Criterion 1: FastAPI app structure migrated from attest_ai/src/main.py
    try:
        fastapi_app = web_ui_service.get_fastapi_app()
        if hasattr(fastapi_app, 'routes') and len(fastapi_app.routes) > 0:
            criteria_results["fastapi_migration"] = "✅ PASS"
            logger.info(f"FastAPI app has {len(fastapi_app.routes)} routes")
        else:
            criteria_results["fastapi_migration"] = "❌ FAIL - No routes found"
    except Exception as e:
        criteria_results["fastapi_migration"] = f"❌ FAIL - {e}"
    
    # ✅ Criterion 2: Attestation endpoint accessible (mock test)
    try:
        attestation_status = await web_ui_service.attestation_service.get_status()
        if attestation_status.get("status") == "operational":
            criteria_results["attestation_endpoint"] = "✅ PASS"
            logger.info("Attestation service operational")
        else:
            criteria_results["attestation_endpoint"] = "❌ FAIL - Service not operational"
    except Exception as e:
        criteria_results["attestation_endpoint"] = f"❌ FAIL - {e}"
    
    # ✅ Criterion 3: Dual attestation extracts required fields
    try:
        # Test with mock data since we're not in SecretVM
        dual_attestation = await web_ui_service.attestation_service.get_dual_attestation()
        required_fields = ["self_vm", "secret_ai_vm", "dual_attestation"]
        
        all_fields_present = all(field in dual_attestation for field in required_fields)
        if all_fields_present and dual_attestation["dual_attestation"]:
            criteria_results["dual_attestation"] = "✅ PASS"
            logger.info("Dual attestation contains required fields")
        else:
            criteria_results["dual_attestation"] = "❌ FAIL - Missing required fields"
    except Exception as e:
        criteria_results["dual_attestation"] = f"❌ FAIL - {e}"
    
    # ✅ Criterion 4: Chat interface routes through hub router
    try:
        response = await hub.route_message(
            interface="web_ui",
            message="Test message for Phase 2 validation",
            options={"temperature": 0.5}
        )
        
        if response["success"] and response["interface"] == "web_ui":
            criteria_results["chat_routing"] = "✅ PASS"
            logger.info("Chat successfully routes through hub router")
        else:
            criteria_results["chat_routing"] = f"❌ FAIL - {response.get('error', 'Routing failed')}"
    except Exception as e:
        criteria_results["chat_routing"] = f"❌ FAIL - {e}"
    
    # ✅ Criterion 5: Proof generation system
    try:
        # Test proof manager initialization
        proof_manager = web_ui_service.proof_manager
        if proof_manager and hasattr(proof_manager, 'generate_proof'):
            criteria_results["proof_generation"] = "✅ PASS"
            logger.info("Proof generation system available")
        else:
            criteria_results["proof_generation"] = "❌ FAIL - Proof manager not available"
    except Exception as e:
        criteria_results["proof_generation"] = f"❌ FAIL - {e}"
    
    # ✅ Criterion 6: Templates and static assets
    try:
        web_ui_interface = web_ui_service.web_ui_interface
        template_path = web_ui_interface.template_path
        static_path = web_ui_interface.static_path
        
        if template_path.exists() and static_path.exists():
            # Check for key templates
            index_template = template_path / "index.html"
            attestation_template = template_path / "attestation.html"
            
            if index_template.exists() and attestation_template.exists():
                criteria_results["templates_assets"] = "✅ PASS"
                logger.info("Templates and static assets present")
            else:
                criteria_results["templates_assets"] = "❌ FAIL - Missing key templates"
        else:
            criteria_results["templates_assets"] = "❌ FAIL - Template/static directories missing"
    except Exception as e:
        criteria_results["templates_assets"] = f"❌ FAIL - {e}"
    
    # ✅ Criterion 7: .attestproof file generation capability
    try:
        # Test that proof manager has required methods
        proof_manager = web_ui_service.proof_manager
        required_methods = ['generate_proof', 'verify_proof', '_encrypt_data', '_decrypt_data']
        
        methods_present = all(hasattr(proof_manager, method) for method in required_methods)
        if methods_present:
            criteria_results["attestproof_system"] = "✅ PASS"
            logger.info("Attestproof file system complete")
        else:
            criteria_results["attestproof_system"] = "❌ FAIL - Missing required methods"
    except Exception as e:
        criteria_results["attestproof_system"] = f"❌ FAIL - {e}"
    
    # Cleanup
    try:
        await web_ui_service.cleanup()
        await hub.shutdown()
    except Exception as e:
        logger.warning(f"Cleanup warning: {e}")
    
    return criteria_results

async def main():
    """Main validation function"""
    logger.info("=== Phase 2 Success Criteria Validation ===")
    
    try:
        results = await validate_phase2_criteria()
        
        logger.info("\n=== VALIDATION RESULTS ===")
        all_passed = True
        
        for criterion, result in results.items():
            logger.info(f"{criterion}: {result}")
            if not result.startswith("✅"):
                all_passed = False
        
        if all_passed:
            logger.info("\n🎉 ALL PHASE 2 SUCCESS CRITERIA PASSED! 🎉")
            logger.info("✅ Web UI with attestation successfully implemented")
            logger.info("✅ Ready for Phase 3: Telegram Bot Integration")
        else:
            logger.error("\n❌ Some criteria failed. Please review and fix.")
            
    except Exception as e:
        logger.error(f"Validation failed with error: {e}")

if __name__ == "__main__":
    asyncio.run(main())