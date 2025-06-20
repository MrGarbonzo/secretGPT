"""
Complete System Validation Script
Tests all secretGPT components end-to-end for production readiness
"""
import asyncio
import logging
import sys
import time
import json
import httpx
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

class SystemValidator:
    """Complete system validation for production readiness"""
    
    def __init__(self):
        self.results = {}
        self.hub = None
        self.secret_ai = None
        self.web_ui_service = None
    
    async def validate_complete_system(self):
        """Run all validation tests"""
        logger.info("=== SECRETGPT COMPLETE SYSTEM VALIDATION ===")
        
        # Initialize system
        await self._initialize_system()
        
        # Core functionality tests
        await self._test_secret_ai_integration()
        await self._test_hub_router_functionality()
        await self._test_environment_configuration()
        await self._test_error_handling()
        
        # Interface integration tests
        await self._test_web_ui_functionality()
        await self._test_cross_interface_consistency()
        
        # Architecture validation
        await self._test_single_container_architecture()
        
        # Production readiness
        await self._test_performance_metrics()
        await self._test_security_measures()
        
        # Cleanup
        await self._cleanup_system()
        
        # Generate final report
        self._generate_validation_report()
    
    async def _initialize_system(self):
        """Initialize all system components"""
        logger.info("Initializing secretGPT system components...")
        
        try:
            # Initialize hub router
            self.hub = HubRouter()
            
            # Initialize Secret AI service
            self.secret_ai = SecretAIService()
            self.hub.register_component(ComponentType.SECRET_AI, self.secret_ai)
            
            # Initialize Web UI service
            self.web_ui_service = WebUIService(self.hub)
            self.hub.register_component(ComponentType.WEB_UI, self.web_ui_service)
            
            # Initialize hub
            await self.hub.initialize()
            
            self.results["system_initialization"] = "✅ PASS"
            logger.info("System initialization: SUCCESS")
            
        except Exception as e:
            self.results["system_initialization"] = f"❌ FAIL - {e}"
            logger.error(f"System initialization: FAILED - {e}")
            raise
    
    async def _test_secret_ai_integration(self):
        """Test Secret AI integration across all interfaces"""
        logger.info("Testing Secret AI integration...")
        
        try:
            # Test model discovery
            available_models = await self.secret_ai.get_available_models()
            if not available_models:
                raise Exception("No models available")
            
            # Test basic chat functionality
            test_message = "Hello, this is a system validation test."
            response = await self.secret_ai.ainvoke([("system", "You are a helpful assistant."), ("human", test_message)])
            
            if not response or not hasattr(response, 'content'):
                raise Exception("Invalid response format")
            
            # Test message formatting
            formatted = self.secret_ai.format_messages("Test system", "Test message")
            if not isinstance(formatted, list) or len(formatted) != 2:
                raise Exception("Message formatting failed")
            
            self.results["secret_ai_integration"] = "✅ PASS"
            logger.info("Secret AI integration: SUCCESS")
            
        except Exception as e:
            self.results["secret_ai_integration"] = f"❌ FAIL - {e}"
            logger.error(f"Secret AI integration: FAILED - {e}")
    
    async def _test_hub_router_functionality(self):
        """Test hub router message routing"""
        logger.info("Testing hub router functionality...")
        
        try:
            # Test web UI routing
            web_response = await self.hub.route_message(
                interface="web_ui",
                message="System validation test for web UI",
                options={"temperature": 0.7}
            )
            
            if not web_response["success"]:
                raise Exception(f"Web UI routing failed: {web_response.get('error')}")
            
            # Test system status
            system_status = await self.hub.get_system_status()
            if system_status["hub"] != "operational":
                raise Exception("Hub not operational")
            
            self.results["hub_router_functionality"] = "✅ PASS"
            logger.info("Hub router functionality: SUCCESS")
            
        except Exception as e:
            self.results["hub_router_functionality"] = f"❌ FAIL - {e}"
            logger.error(f"Hub router functionality: FAILED - {e}")
    
    async def _test_environment_configuration(self):
        """Test environment variable configuration"""
        logger.info("Testing environment configuration...")
        
        try:
            # Validate settings
            if not validate_settings():
                raise Exception("Settings validation failed")
            
            # Check required environment variables
            required_vars = [
                "SECRET_AI_API_KEY",
            ]
            
            for var in required_vars:
                if not getattr(settings, var.lower(), None):
                    raise Exception(f"Missing required environment variable: {var}")
            
            self.results["environment_configuration"] = "✅ PASS"
            logger.info("Environment configuration: SUCCESS")
            
        except Exception as e:
            self.results["environment_configuration"] = f"❌ FAIL - {e}"
            logger.error(f"Environment configuration: FAILED - {e}")
    
    async def _test_error_handling(self):
        """Test error handling across components"""
        logger.info("Testing error handling...")
        
        try:
            # Test hub error handling with invalid interface
            error_response = await self.hub.route_message(
                interface="invalid_interface",
                message="Test error handling",
                options={}
            )
            
            if error_response["success"]:
                raise Exception("Error handling failed - should have returned error")
            
            # Test web UI service error handling
            web_ui_status = await self.web_ui_service.get_status()
            if "error" in web_ui_status and web_ui_status["error"]:
                logger.warning(f"Web UI has errors: {web_ui_status['error']}")
            
            self.results["error_handling"] = "✅ PASS"
            logger.info("Error handling: SUCCESS")
            
        except Exception as e:
            self.results["error_handling"] = f"❌ FAIL - {e}"
            logger.error(f"Error handling: FAILED - {e}")
    
    async def _test_web_ui_functionality(self):
        """Test web UI functionality"""
        logger.info("Testing web UI functionality...")
        
        try:
            # Test web UI service status
            status = await self.web_ui_service.get_status()
            if status["status"] != "operational":
                raise Exception(f"Web UI not operational: {status}")
            
            # Test attestation service
            attestation_status = status.get("components", {}).get("attestation")
            if attestation_status != "operational":
                logger.warning("Attestation service not fully operational (expected in non-SecretVM environment)")
            
            # Test proof manager
            proof_manager_status = status.get("components", {}).get("proof_manager")
            if proof_manager_status != "operational":
                raise Exception("Proof manager not operational")
            
            # Test FastAPI app availability
            app = self.web_ui_service.get_fastapi_app()
            if not app:
                raise Exception("FastAPI app not available")
            
            self.results["web_ui_functionality"] = "✅ PASS"
            logger.info("Web UI functionality: SUCCESS")
            
        except Exception as e:
            self.results["web_ui_functionality"] = f"❌ FAIL - {e}"
            logger.error(f"Web UI functionality: FAILED - {e}")
    
    
    async def _test_cross_interface_consistency(self):
        """Test consistency across interfaces"""
        logger.info("Testing cross-interface consistency...")
        
        try:
            test_message = "What is confidential computing?"
            
            # Get response from web UI interface
            web_response = await self.hub.route_message(
                interface="web_ui",
                message=test_message,
                options={"temperature": 0.5}
            )
            
            # Verify response
            if not web_response["success"]:
                raise Exception("Interface response failed")
            
            # Should have content
            if not web_response["content"]:
                raise Exception("Missing response content")
            
            # Should be from the correct interface attribution
            if web_response["interface"] != "web_ui":
                raise Exception("Interface attribution incorrect")
            
            self.results["cross_interface_consistency"] = "✅ PASS"
            logger.info("Cross-interface consistency: SUCCESS")
            
        except Exception as e:
            self.results["cross_interface_consistency"] = f"❌ FAIL - {e}"
            logger.error(f"Cross-interface consistency: FAILED - {e}")
    
    async def _test_single_container_architecture(self):
        """Test single container architecture validation"""
        logger.info("Testing single container architecture...")
        
        try:
            # Test that all services can coexist
            all_services = [self.secret_ai, self.web_ui_service]
            
            for service in all_services:
                if hasattr(service, 'get_status'):
                    status = await service.get_status()
                    logger.info(f"Service {service.__class__.__name__}: {status.get('status', 'unknown')}")
            
            # Test resource sharing (hub router)
            hub_status = await self.hub.get_system_status()
            components = hub_status.get("components", {})
            
            if len(components) < 2:  # At least secret_ai and web_ui
                raise Exception("Not all components registered with hub")
            
            self.results["single_container_architecture"] = "✅ PASS"
            logger.info("Single container architecture: SUCCESS")
            
        except Exception as e:
            self.results["single_container_architecture"] = f"❌ FAIL - {e}"
            logger.error(f"Single container architecture: FAILED - {e}")
    
    async def _test_performance_metrics(self):
        """Test basic performance metrics"""
        logger.info("Testing performance metrics...")
        
        try:
            # Test response time
            start_time = time.time()
            response = await self.hub.route_message(
                interface="web_ui",
                message="Quick performance test",
                options={"temperature": 0.1}
            )
            response_time = time.time() - start_time
            
            if not response["success"]:
                raise Exception("Performance test failed")
            
            logger.info(f"Response time: {response_time:.2f} seconds")
            
            # Test concurrent requests (simplified)
            tasks = []
            for i in range(3):
                task = self.hub.route_message(
                    interface="web_ui",
                    message=f"Concurrent test {i}",
                    options={"temperature": 0.1}
                )
                tasks.append(task)
            
            concurrent_start = time.time()
            results = await asyncio.gather(*tasks)
            concurrent_time = time.time() - concurrent_start
            
            failed_requests = sum(1 for r in results if not r["success"])
            if failed_requests > 0:
                logger.warning(f"{failed_requests} concurrent requests failed")
            
            logger.info(f"Concurrent requests time: {concurrent_time:.2f} seconds")
            
            self.results["performance_metrics"] = "✅ PASS"
            logger.info("Performance metrics: SUCCESS")
            
        except Exception as e:
            self.results["performance_metrics"] = f"❌ FAIL - {e}"
            logger.error(f"Performance metrics: FAILED - {e}")
    
    async def _test_security_measures(self):
        """Test security measures"""
        logger.info("Testing security measures...")
        
        try:
            # Test API key protection
            if settings.secret_ai_api_key and len(settings.secret_ai_api_key) < 10:
                raise Exception("API key appears to be invalid or test key")
            
            # Test input validation (basic)
            malicious_inputs = [
                "'; DROP TABLE users; --",
                "<script>alert('xss')</script>",
                "../../etc/passwd",
                "\x00\x01\x02"
            ]
            
            for malicious_input in malicious_inputs:
                try:
                    response = await self.hub.route_message(
                        interface="web_ui",
                        message=malicious_input,
                        options={}
                    )
                    # Should not crash or expose sensitive info
                    if response["success"] and "error" in response["content"].lower():
                        logger.warning("Potential error exposure in response")
                except Exception:
                    # Graceful error handling is expected
                    pass
            
            self.results["security_measures"] = "✅ PASS"
            logger.info("Security measures: SUCCESS")
            
        except Exception as e:
            self.results["security_measures"] = f"❌ FAIL - {e}"
            logger.error(f"Security measures: FAILED - {e}")
    
    async def _cleanup_system(self):
        """Cleanup system resources"""
        logger.info("Cleaning up system resources...")
        
        try:
            if self.web_ui_service:
                await self.web_ui_service.cleanup()
            
            if self.hub:
                await self.hub.shutdown()
            
            logger.info("System cleanup: SUCCESS")
            
        except Exception as e:
            logger.warning(f"Cleanup warning: {e}")
    
    def _generate_validation_report(self):
        """Generate final validation report"""
        logger.info("\n=== SECRETGPT SYSTEM VALIDATION REPORT ===")
        
        total_tests = len(self.results)
        passed_tests = sum(1 for result in self.results.values() if result.startswith("✅"))
        
        logger.info(f"Total Tests: {total_tests}")
        logger.info(f"Passed: {passed_tests}")
        logger.info(f"Failed: {total_tests - passed_tests}")
        logger.info(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        logger.info("\n=== DETAILED RESULTS ===")
        for test_name, result in self.results.items():
            logger.info(f"{test_name}: {result}")
        
        # Overall assessment
        if passed_tests == total_tests:
            logger.info("\n🎉 ALL TESTS PASSED - SYSTEM READY FOR PRODUCTION!")
        elif passed_tests >= total_tests * 0.8:
            logger.info("\n⚠️  MOST TESTS PASSED - SYSTEM READY WITH MINOR ISSUES")
        else:
            logger.info("\n❌ MULTIPLE FAILURES - SYSTEM NOT READY FOR PRODUCTION")
        
        return self.results

async def main():
    """Main validation function"""
    validator = SystemValidator()
    await validator.validate_complete_system()

if __name__ == "__main__":
    asyncio.run(main())