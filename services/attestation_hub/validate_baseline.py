#!/usr/bin/env python3
"""Validate attestation hub against baseline data"""

import asyncio
import json
import logging
from pathlib import Path
import sys

from parsers.hardcoded import HardcodedParser
from config.settings import VMConfig

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def validate_baseline():
    """Validate parsing against baseline data"""
    
    # Load baseline data
    baseline_file = Path(__file__).parent.parent.parent / "experiments/attest_tool_research/findings/current_parser_baseline.json"
    if not baseline_file.exists():
        logger.error(f"Baseline file not found: {baseline_file}")
        return False
    
    with open(baseline_file, 'r') as f:
        baseline = json.load(f)
    
    # Load test quote
    quote_file = Path(__file__).parent.parent.parent / "experiments/attest_tool_research/sample_data/known_good_quote.hex"
    if not quote_file.exists():
        logger.error(f"Test quote file not found: {quote_file}")
        return False
    
    with open(quote_file, 'r') as f:
        test_quote = f.read().strip()
    
    logger.info(f"Loaded test quote: {len(test_quote)} characters")
    logger.info(f"Baseline data: {len(baseline)} fields")
    
    # Test hardcoded parser
    parser = HardcodedParser()
    vm_config = VMConfig(
        endpoint="https://localhost:29343",
        type="secret-gpt",
        parsing_strategy="hardcoded"
    )
    
    try:
        # Parse the quote
        attestation = await parser.parse_attestation(test_quote, vm_config, "test_cert")
        
        # Compare with baseline
        validation_results = {
            "mrtd_match": attestation.mrtd == baseline["mrtd"],
            "rtmr0_match": attestation.rtmr0 == baseline["rtmr0"],
            "rtmr1_match": attestation.rtmr1 == baseline["rtmr1"],
            "rtmr2_match": attestation.rtmr2 == baseline["rtmr2"],
            "rtmr3_match": attestation.rtmr3 == baseline["rtmr3"],
            "report_data_match": attestation.report_data == baseline["report_data"],
        }
        
        all_match = all(validation_results.values())
        
        logger.info("=== BASELINE VALIDATION RESULTS ===")
        for field, matches in validation_results.items():
            status = "✅ PASS" if matches else "❌ FAIL"
            logger.info(f"{field}: {status}")
        
        logger.info(f"\nOverall validation: {'✅ PASS' if all_match else '❌ FAIL'}")
        
        if not all_match:
            logger.error("\n=== MISMATCHES ===")
            for field, matches in validation_results.items():
                if not matches:
                    field_name = field.replace('_match', '')
                    baseline_val = baseline.get(field_name, "")
                    actual_val = getattr(attestation, field_name, "")
                    
                    logger.error(f"{field_name}:")
                    logger.error(f"  Expected: {baseline_val[:64]}...")
                    logger.error(f"  Actual:   {actual_val[:64]}...")
        
        # Additional validation
        logger.info("\n=== FIELD LENGTH VALIDATION ===")
        length_checks = {
            "mrtd": (len(attestation.mrtd), 96),
            "rtmr0": (len(attestation.rtmr0), 96),
            "rtmr1": (len(attestation.rtmr1), 96),
            "rtmr2": (len(attestation.rtmr2), 96),
            "rtmr3": (len(attestation.rtmr3), 96),
            "report_data": (len(attestation.report_data), 64),
        }
        
        for field, (actual_len, expected_len) in length_checks.items():
            status = "✅ PASS" if actual_len == expected_len else "❌ FAIL"
            logger.info(f"{field} length: {actual_len} (expected {expected_len}) {status}")
        
        logger.info("\n=== METADATA VALIDATION ===")
        logger.info(f"VM name: {attestation.vm_name}")
        logger.info(f"VM type: {attestation.vm_type}")
        logger.info(f"Parsing method: {attestation.parsing_method}")
        logger.info(f"Certificate fingerprint: {attestation.certificate_fingerprint}")
        logger.info(f"Timestamp: {attestation.timestamp}")
        
        return all_match
        
    except Exception as e:
        logger.error(f"Validation failed with exception: {e}")
        return False


async def test_service_startup():
    """Test basic service components"""
    
    logger.info("\n=== SERVICE COMPONENT TEST ===")
    
    try:
        # Test configuration loading
        from config.settings import ConfigManager
        config_manager = ConfigManager()
        logger.info("✅ Configuration manager initialized")
        
        # Test VM manager
        from hub.vm_manager import VMManager
        vm_manager = VMManager(config_manager)
        vms = vm_manager.list_vms()
        logger.info(f"✅ VM manager initialized with {len(vms)} VMs: {list(vms.keys())}")
        
        # Test parser factory
        from parsers.base import ParserFactory
        import parsers.hardcoded
        import parsers.rest_server
        
        parsers = ParserFactory.list_parsers()
        logger.info(f"✅ Parser factory with {len(parsers)} parsers: {parsers}")
        
        # Test attestation hub
        from hub.service import AttestationHub
        hub = AttestationHub(config_manager)
        health = hub.get_service_health()
        logger.info(f"✅ Attestation hub initialized, status: {health.status.value}")
        
        await hub.cleanup()
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Service component test failed: {e}")
        return False


async def main():
    """Run all validation tests"""
    
    logger.info("Starting Attestation Hub Validation")
    logger.info("=" * 50)
    
    # Test 1: Baseline validation
    baseline_pass = await validate_baseline()
    
    # Test 2: Service component test
    service_pass = await test_service_startup()
    
    logger.info("\n" + "=" * 50)
    logger.info("VALIDATION SUMMARY")
    logger.info("=" * 50)
    
    logger.info(f"Baseline validation: {'✅ PASS' if baseline_pass else '❌ FAIL'}")
    logger.info(f"Service components: {'✅ PASS' if service_pass else '❌ FAIL'}")
    
    overall_pass = baseline_pass and service_pass
    logger.info(f"Overall validation: {'✅ PASS' if overall_pass else '❌ FAIL'}")
    
    if overall_pass:
        logger.info("\n🎉 Attestation Hub is ready for deployment!")
        return 0
    else:
        logger.error("\n❌ Validation failed - fix issues before deployment")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)