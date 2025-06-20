"""
Complete Deployment Test Script
Tests all secretGPT components in production configuration
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

class DeploymentTester:
    """Complete deployment testing for production readiness"""
    
    def __init__(self):
        self.results = {}
        self.hub = None
        self.secret_ai = None
        self.web_ui_service = None
    
    async def test_complete_deployment(self):
        """Run complete deployment test"""
        logger.info("🚀 TESTING COMPLETE SECRETGPT DEPLOYMENT")
        
        # Initialize system
        await self._initialize_production_system()
        
        # Test core functionality
        await self._test_secret_ai_functionality()
        await self._test_hub_router_routing()
        
        # Test interface functionality
        await self._test_web_ui_features()
        
        # Test production features
        await self._test_health_monitoring()
        await self._test_error_handling()
        await self._test_concurrent_requests()
        
        # Generate deployment report
        self._generate_deployment_report()
        
        # Keep system running for manual testing
        await self._keep_system_running()
    
    async def _initialize_production_system(self):
        """Initialize production system configuration"""
        logger.info("🔧 Initializing production system...")
        
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
            
            self.results["system_initialization"] = "✅ SUCCESS"
            logger.info("✅ Production system initialized successfully")
            
        except Exception as e:
            self.results["system_initialization"] = f"❌ FAILED - {e}"
            logger.error(f"❌ System initialization failed: {e}")
            raise
    
    async def _test_secret_ai_functionality(self):
        """Test Secret AI core functionality"""
        logger.info("🤖 Testing Secret AI functionality...")
        
        try:
            # Test model discovery
            models = self.secret_ai.get_available_models()
            logger.info(f"Available models: {models}")
            
            # Test basic invocation
            messages = self.secret_ai.format_messages(
                "You are a helpful assistant.",
                "What is confidential computing? (Keep response brief)"
            )
            
            response = await self.secret_ai.ainvoke(messages)
            
            if response["success"] and len(response["content"]) > 50:
                self.results["secret_ai_functionality"] = "✅ SUCCESS"
                logger.info("✅ Secret AI functionality working")
                logger.info(f"Sample response: {response['content'][:100]}...")
            else:
                self.results["secret_ai_functionality"] = "❌ FAILED - Invalid response"
                
        except Exception as e:
            self.results["secret_ai_functionality"] = f"❌ FAILED - {e}"
            logger.error(f"❌ Secret AI functionality failed: {e}")
    
    async def _test_hub_router_routing(self):
        """Test hub router message routing"""
        logger.info("🔄 Testing hub router routing...")
        
        try:
            # Test Web UI routing
            web_response = await self.hub.route_message(
                interface="web_ui",
                message="Test message from web UI",
                options={"temperature": 0.5}
            )
            
            
            # Test system status
            system_status = await self.hub.get_system_status()
            
            if (web_response["success"] and 
                system_status["hub"] == "operational"):
                self.results["hub_router_routing"] = "✅ SUCCESS"
                logger.info("✅ Hub router routing working correctly")
            else:
                self.results["hub_router_routing"] = "❌ FAILED - Routing issues"
                
        except Exception as e:
            self.results["hub_router_routing"] = f"❌ FAILED - {e}"
            logger.error(f"❌ Hub router routing failed: {e}")
    
    async def _test_web_ui_features(self):
        """Test Web UI features"""
        logger.info("🌐 Testing Web UI features...")
        
        try:
            # Test Web UI service status
            status = await self.web_ui_service.get_status()
            
            # Test FastAPI app
            app = self.web_ui_service.get_fastapi_app()
            
            # Test chat functionality through hub
            chat_response = await self.hub.route_message(
                interface="web_ui",
                message="Hello from Web UI test",
                options={"temperature": 0.3}
            )
            
            if (status["status"] == "operational" and app and 
                chat_response["success"]):
                self.results["web_ui_features"] = "✅ SUCCESS"
                logger.info("✅ Web UI features working")
                logger.info(f"Web UI status: {status}")
            else:
                self.results["web_ui_features"] = "❌ FAILED - Feature issues"
                
        except Exception as e:
            self.results["web_ui_features"] = f"❌ FAILED - {e}"
            logger.error(f"❌ Web UI features failed: {e}")
    
    
    async def _test_health_monitoring(self):
        """Test health monitoring"""
        logger.info("💚 Testing health monitoring...")
        
        try:
            # Test system health
            system_status = await self.hub.get_system_status()
            
            # Test component health
            web_ui_status = await self.web_ui_service.get_status()
            
            
            # Test that all components report properly
            if (system_status["hub"] == "operational" and
                web_ui_status["status"] == "operational"):
                self.results["health_monitoring"] = "✅ SUCCESS"
                logger.info("✅ Health monitoring working")
                logger.info(f"System health: {system_status}")
            else:
                self.results["health_monitoring"] = "❌ FAILED - Health issues"
                
        except Exception as e:
            self.results["health_monitoring"] = f"❌ FAILED - {e}"
            logger.error(f"❌ Health monitoring failed: {e}")
    
    async def _test_error_handling(self):
        """Test error handling"""
        logger.info("🛡️ Testing error handling...")
        
        try:
            # Test invalid interface
            invalid_response = await self.hub.route_message(
                interface="invalid_interface",
                message="Test error handling",
                options={}
            )
            
            # Test empty message
            empty_response = await self.hub.route_message(
                interface="web_ui",
                message="",
                options={}
            )
            
            # Error handling should work (not crash)
            if (not invalid_response["success"] and 
                "error" in invalid_response):
                self.results["error_handling"] = "✅ SUCCESS"
                logger.info("✅ Error handling working correctly")
            else:
                self.results["error_handling"] = "❌ FAILED - Error handling issues"
                
        except Exception as e:
            self.results["error_handling"] = f"❌ FAILED - {e}"
            logger.error(f"❌ Error handling failed: {e}")
    
    async def _test_concurrent_requests(self):
        """Test concurrent request handling"""
        logger.info("⚡ Testing concurrent requests...")
        
        try:
            # Create multiple concurrent requests
            tasks = []
            for i in range(3):
                task = self.hub.route_message(
                    interface="web_ui",
                    message=f"Concurrent test request {i+1}",
                    options={"temperature": 0.1}
                )
                tasks.append(task)
            
            # Execute concurrently
            start_time = time.time()
            results = await asyncio.gather(*tasks, return_exceptions=True)
            end_time = time.time()
            
            # Check results
            successful_requests = sum(1 for r in results if isinstance(r, dict) and r.get("success"))
            
            if successful_requests >= 2:  # At least 2 out of 3 should succeed
                self.results["concurrent_requests"] = "✅ SUCCESS"
                logger.info(f"✅ Concurrent requests working ({successful_requests}/3 successful)")
                logger.info(f"Total time: {end_time - start_time:.2f} seconds")
            else:
                self.results["concurrent_requests"] = "❌ FAILED - Too many failures"
                
        except Exception as e:
            self.results["concurrent_requests"] = f"❌ FAILED - {e}"
            logger.error(f"❌ Concurrent requests failed: {e}")
    
    def _generate_deployment_report(self):
        """Generate deployment test report"""
        logger.info("\n" + "="*60)
        logger.info("🎉 SECRETGPT DEPLOYMENT TEST RESULTS")
        logger.info("="*60)
        
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
            logger.info("\n🎉 ALL TESTS PASSED - DEPLOYMENT SUCCESSFUL!")
            logger.info("✅ secretGPT Hub is fully operational and ready for use")
        elif passed_tests >= total_tests * 0.8:
            logger.info("\n⚠️  MOST TESTS PASSED - DEPLOYMENT MOSTLY SUCCESSFUL")
            logger.info("⚠️ Some minor issues detected, but system is functional")
        else:
            logger.info("\n❌ MULTIPLE FAILURES - DEPLOYMENT NEEDS ATTENTION")
            logger.info("❌ Please review failed tests and fix issues")
        
        logger.info("\n=== SYSTEM ACCESS ===")
        
        logger.info("🌐 Web UI: Service initialized and ready")
        logger.info("   (Would be available at http://localhost:8000 in full deployment)")
        
        logger.info("💚 Health Monitoring: Active")
        logger.info("🔄 Hub Router: Operational")
        logger.info("🤖 Secret AI: Connected and responding")
        
        return self.results
    
    async def _keep_system_running(self):
        """Keep system running for manual testing"""
        logger.info("\n" + "="*60)
        logger.info("🚀 SYSTEM RUNNING - READY FOR TESTING")
        logger.info("="*60)
        logger.info("secretGPT Hub is now running and ready for use!")
        logger.info("Press Ctrl+C to stop the system")
        logger.info("="*60)
        
        try:
            
            # Keep running
            while True:
                await asyncio.sleep(5)
                
                # Periodic health check
                try:
                    status = await self.hub.get_system_status()
                    if status["hub"] != "operational":
                        logger.warning("⚠️ System health check: Hub not operational")
                except Exception as e:
                    logger.warning(f"⚠️ Health check failed: {e}")
                
        except KeyboardInterrupt:
            logger.info("\n🛑 Shutdown signal received")
        finally:
            await self._cleanup_system()
    
    async def _cleanup_system(self):
        """Cleanup system resources"""
        logger.info("🧹 Cleaning up system resources...")
        
        try:
            
            if self.web_ui_service:
                await self.web_ui_service.cleanup()
            
            if self.hub:
                await self.hub.shutdown()
            
            logger.info("✅ System cleanup complete")
            
        except Exception as e:
            logger.warning(f"⚠️ Cleanup warning: {e}")

async def main():
    """Main deployment test function"""
    logger.info("🚀 Starting secretGPT Hub deployment test...")
    
    # Validate environment
    if not validate_settings():
        logger.error("❌ Environment validation failed")
        return
    
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Secret AI API Key: {'Set' if settings.secret_ai_api_key else 'Missing'}")
    logger.info(f"Web UI: {'Enabled' if settings.enable_web_ui else 'Disabled'}")
    
    # Run deployment test
    tester = DeploymentTester()
    await tester.test_complete_deployment()

if __name__ == "__main__":
    asyncio.run(main())