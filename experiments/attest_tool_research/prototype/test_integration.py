#!/usr/bin/env python3
"""
Integration Test Script for Enhanced Attestation Service

This script tests the secret-vm-attest-rest-server integration and validates
the output against your current parsing baseline.
"""

import asyncio
import json
import sys
from pathlib import Path

# Add the tools directory to the path
sys.path.append(str(Path(__file__).parent.parent / "tools"))

try:
    from enhanced_attestation_service import EnhancedAttestationService, AttestationError
except ImportError:
    from prototype.enhanced_attestation_service import EnhancedAttestationService, AttestationError

class IntegrationTester:
    """Test the enhanced attestation service integration"""
    
    def __init__(self):
        self.baseline_file = Path(__file__).parent.parent / "findings" / "current_parser_baseline.json"
        self.quote_file = Path(__file__).parent.parent / "sample_data" / "known_good_quote.hex"
        self.baseline = None
        self.quote = None
        
    def load_test_data(self):
        """Load baseline and test quote data"""
        try:
            with open(self.baseline_file, 'r') as f:
                self.baseline = json.load(f)
            print(f"✅ Loaded baseline from {self.baseline_file}")
            
            with open(self.quote_file, 'r') as f:
                self.quote = f.read().strip()
            print(f"✅ Loaded quote from {self.quote_file} ({len(self.quote)} chars)")
            
        except Exception as e:
            print(f"❌ Failed to load test data: {e}")
            return False
        
        return True
    
    async def test_rest_server_connectivity(self):
        """Test REST server connectivity"""
        print("\n🔗 Testing REST Server Connectivity...")
        
        service = EnhancedAttestationService()
        
        try:
            status = await service.get_status()
            print(f"📊 Service Status: {json.dumps(status, indent=2)}")
            
            if status.get("rest_server_status") == "online":
                print("✅ REST server is online and responding")
                return True
            else:
                print(f"⚠️ REST server status: {status.get('rest_server_status')}")
                print(f"   Error: {status.get('rest_server_error', 'Unknown')}")
                return False
                
        except Exception as e:
            print(f"❌ REST server connectivity test failed: {e}")
            return False
        finally:
            await service.cleanup()
    
    async def test_parsing_accuracy(self):
        """Test parsing accuracy against baseline"""
        print("\n🧪 Testing Parsing Accuracy...")
        
        service = EnhancedAttestationService()
        
        try:
            # Parse the quote
            result = await service.parse_attestation_quote(self.quote, "test_cert", "test_vm")
            
            # Compare with baseline
            comparison = {
                'mrtd': result.mrtd == self.baseline['mrtd'],
                'rtmr0': result.rtmr0 == self.baseline['rtmr0'],
                'rtmr1': result.rtmr1 == self.baseline['rtmr1'],
                'rtmr2': result.rtmr2 == self.baseline['rtmr2'],
                'rtmr3': result.rtmr3 == self.baseline['rtmr3'],
                'report_data': result.report_data == self.baseline['report_data']
            }
            
            print(f"📊 Field Comparison Results:")
            all_match = True
            for field, matches in comparison.items():
                status_icon = "✅" if matches else "❌"
                print(f"   {status_icon} {field}: {'MATCH' if matches else 'MISMATCH'}")
                if not matches:
                    all_match = False
                    baseline_val = self.baseline[field]
                    result_val = getattr(result, field)
                    print(f"      Baseline: {baseline_val[:32]}...")
                    print(f"      Result:   {result_val[:32]}...")
            
            if all_match:
                print("🎉 All fields match baseline - parsing accuracy confirmed!")
            else:
                print("⚠️ Some fields don't match - may indicate parsing differences")
            
            return all_match
            
        except Exception as e:
            print(f"❌ Parsing accuracy test failed: {e}")
            return False
        finally:
            await service.cleanup()
    
    async def test_performance(self):
        """Test parsing performance"""
        print("\n⚡ Testing Performance...")
        
        service = EnhancedAttestationService()
        
        try:
            import time
            
            # Warm up
            await service.parse_attestation_quote(self.quote, "test_cert", "warmup")
            
            # Performance test
            iterations = 5
            times = []
            
            for i in range(iterations):
                start_time = time.time()
                await service.parse_attestation_quote(self.quote, "test_cert", f"perf_test_{i}")
                end_time = time.time()
                times.append(end_time - start_time)
            
            avg_time = sum(times) / len(times)
            min_time = min(times)
            max_time = max(times)
            
            print(f"📊 Performance Results ({iterations} iterations):")
            print(f"   Average: {avg_time:.3f}s")
            print(f"   Min:     {min_time:.3f}s")
            print(f"   Max:     {max_time:.3f}s")
            
            if avg_time < 10.0:
                print("✅ Performance meets requirements (< 10s)")
                return True
            else:
                print("⚠️ Performance slower than expected (> 10s)")
                return False
                
        except Exception as e:
            print(f"❌ Performance test failed: {e}")
            return False
        finally:
            await service.cleanup()
    
    async def test_error_handling(self):
        """Test error handling with invalid inputs"""
        print("\n🛡️ Testing Error Handling...")
        
        service = EnhancedAttestationService()
        
        test_cases = [
            ("empty_quote", ""),
            ("short_quote", "1234567890"),
            ("invalid_hex", "invalid_hex_data"),
            ("truncated_quote", self.quote[:1000])
        ]
        
        passed = 0
        
        for test_name, test_quote in test_cases:
            try:
                result = await service.parse_attestation_quote(test_quote, "test_cert", test_name)
                
                # Should not reach here for invalid inputs
                print(f"   ⚠️ {test_name}: Unexpectedly succeeded")
                
            except AttestationError as e:
                print(f"   ✅ {test_name}: Properly handled error - {str(e)[:50]}...")
                passed += 1
            except Exception as e:
                print(f"   ❌ {test_name}: Unexpected error type - {type(e).__name__}")
        
        await service.cleanup()
        
        print(f"📊 Error Handling: {passed}/{len(test_cases)} tests passed")
        return passed == len(test_cases)
    
    async def run_all_tests(self):
        """Run comprehensive integration tests"""
        print("🚀 Starting Enhanced Attestation Service Integration Tests")
        print("=" * 60)
        
        # Load test data
        if not self.load_test_data():
            print("❌ Test data loading failed - cannot continue")
            return False
        
        # Run tests
        test_results = []
        
        # Test 1: REST server connectivity
        connectivity_ok = await self.test_rest_server_connectivity()
        test_results.append(("REST Server Connectivity", connectivity_ok))
        
        # Test 2: Parsing accuracy
        accuracy_ok = await self.test_parsing_accuracy()
        test_results.append(("Parsing Accuracy", accuracy_ok))
        
        # Test 3: Performance
        performance_ok = await self.test_performance()
        test_results.append(("Performance", performance_ok))
        
        # Test 4: Error handling
        error_handling_ok = await self.test_error_handling()
        test_results.append(("Error Handling", error_handling_ok))
        
        # Summary
        print("\n" + "=" * 60)
        print("🏁 Integration Test Summary")
        print("=" * 60)
        
        all_passed = True
        for test_name, passed in test_results:
            status_icon = "✅" if passed else "❌"
            print(f"{status_icon} {test_name}: {'PASSED' if passed else 'FAILED'}")
            if not passed:
                all_passed = False
        
        if all_passed:
            print("\n🎉 All tests passed! Integration is ready for production.")
            print("\n📋 Next Steps:")
            print("   1. Deploy secret-vm-attest-rest-server on your SecretVM")
            print("   2. Update secretGPT to use EnhancedAttestationService")
            print("   3. Configure feature flags for gradual rollout")
            print("   4. Monitor performance and accuracy in production")
        else:
            print("\n⚠️ Some tests failed. Review the issues before proceeding.")
            print("\n📋 Troubleshooting:")
            print("   1. Ensure secret-vm-attest-rest-server is running on port 29343")
            print("   2. Check TLS certificates and network connectivity")
            print("   3. Verify attest_tool is available on the SecretVM")
            print("   4. Consider fallback to hardcoded parsing if needed")
        
        return all_passed


async def main():
    """Main test function"""
    tester = IntegrationTester()
    success = await tester.run_all_tests()
    return 0 if success else 1


if __name__ == "__main__":
    import sys
    sys.exit(asyncio.run(main()))
