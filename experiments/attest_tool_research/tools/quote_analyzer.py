#!/usr/bin/env python3
"""
Quote Analyzer - Tool for testing attest_tool with different quotes

This script helps analyze and test the attest_tool with various quote inputs
to understand its interface, output format, and error handling.
"""

import subprocess
import json
import sys
import os
import time
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AttestToolAnalyzer:
    """Analyzer for attest_tool interface and behavior"""
    
    def __init__(self, attest_tool_path: str = "./tools/attest_tool"):
        self.attest_tool_path = attest_tool_path
        self.results = []
        
    def test_basic_execution(self) -> Dict[str, Any]:
        """Test basic attest_tool execution"""
        logger.info("Testing basic attest_tool execution...")
        
        tests = [
            {"cmd": ["--help"], "desc": "Help command"},
            {"cmd": ["-h"], "desc": "Short help"},
            {"cmd": ["--version"], "desc": "Version command"},
            {"cmd": ["-v"], "desc": "Short version"},
            {"cmd": [], "desc": "No arguments"}
        ]
        
        results = {}
        
        for test in tests:
            try:
                result = subprocess.run(
                    [self.attest_tool_path] + test["cmd"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                results[test["desc"]] = {
                    "success": True,
                    "return_code": result.returncode,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "command": test["cmd"]
                }
                
                logger.info(f"✅ {test['desc']}: Return code {result.returncode}")
                
            except subprocess.TimeoutExpired:
                results[test["desc"]] = {
                    "success": False,
                    "error": "Timeout after 10 seconds",
                    "command": test["cmd"]
                }
                logger.error(f"❌ {test['desc']}: Timeout")
                
            except FileNotFoundError:
                results[test["desc"]] = {
                    "success": False,
                    "error": f"attest_tool not found at {self.attest_tool_path}",
                    "command": test["cmd"]
                }
                logger.error(f"❌ {test['desc']}: Tool not found")
                
            except Exception as e:
                results[test["desc"]] = {
                    "success": False,
                    "error": str(e),
                    "command": test["cmd"]
                }
                logger.error(f"❌ {test['desc']}: {e}")
        
        return results
    
    def test_input_formats(self, quote_file: str) -> Dict[str, Any]:
        """Test different input format options"""
        logger.info(f"Testing input formats with {quote_file}...")
        
        if not os.path.exists(quote_file):
            logger.error(f"Quote file not found: {quote_file}")
            return {"error": f"Quote file not found: {quote_file}"}
        
        tests = [
            {"cmd": ["--input", quote_file], "desc": "Long input flag"},
            {"cmd": ["-i", quote_file], "desc": "Short input flag"},
            {"cmd": [quote_file], "desc": "Positional argument"},
        ]
        
        results = {}
        
        for test in tests:
            try:
                result = subprocess.run(
                    [self.attest_tool_path] + test["cmd"],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                results[test["desc"]] = {
                    "success": result.returncode == 0,
                    "return_code": result.returncode,
                    "stdout": result.stdout[:500] + "..." if len(result.stdout) > 500 else result.stdout,
                    "stderr": result.stderr,
                    "command": test["cmd"]
                }
                
                status = "✅" if result.returncode == 0 else "❌"
                logger.info(f"{status} {test['desc']}: Return code {result.returncode}")
                
            except Exception as e:
                results[test["desc"]] = {
                    "success": False,
                    "error": str(e),
                    "command": test["cmd"]
                }
                logger.error(f"❌ {test['desc']}: {e}")
        
        return results
    
    def test_output_formats(self, quote_file: str) -> Dict[str, Any]:
        """Test different output format options"""
        logger.info(f"Testing output formats with {quote_file}...")
        
        if not os.path.exists(quote_file):
            logger.error(f"Quote file not found: {quote_file}")
            return {"error": f"Quote file not found: {quote_file}"}
        
        formats = ["json", "text", "raw", "xml", "yaml"]
        
        results = {}
        
        for fmt in formats:
            try:
                # Test with --output-format
                result = subprocess.run([
                    self.attest_tool_path,
                    "--input", quote_file,
                    "--output-format", fmt
                ], capture_output=True, text=True, timeout=30)
                
                results[f"format_{fmt}"] = {
                    "success": result.returncode == 0,
                    "return_code": result.returncode,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "format": fmt
                }
                
                status = "✅" if result.returncode == 0 else "❌"
                logger.info(f"{status} Output format '{fmt}': Return code {result.returncode}")
                
                # Try to parse JSON if format is json
                if fmt == "json" and result.returncode == 0:
                    try:
                        parsed = json.loads(result.stdout)
                        results[f"format_{fmt}"]["parsed_json"] = parsed
                        logger.info(f"✅ JSON parsing successful for format '{fmt}'")
                    except json.JSONDecodeError as e:
                        results[f"format_{fmt}"]["json_parse_error"] = str(e)
                        logger.warning(f"⚠️ JSON parsing failed for format '{fmt}': {e}")
                        
            except Exception as e:
                results[f"format_{fmt}"] = {
                    "success": False,
                    "error": str(e),
                    "format": fmt
                }
                logger.error(f"❌ Output format '{fmt}': {e}")
        
        return results
    
    def test_error_scenarios(self) -> Dict[str, Any]:
        """Test error handling with various problematic inputs"""
        logger.info("Testing error scenarios...")
        
        test_files = [
            "../sample_data/empty_quote.hex",
            "../sample_data/invalid_quote.hex", 
            "../sample_data/truncated_quote.hex",
            "nonexistent_file.hex"
        ]
        
        results = {}
        
        for test_file in test_files:
            try:
                result = subprocess.run([
                    self.attest_tool_path,
                    "--input", test_file,
                    "--output-format", "json"
                ], capture_output=True, text=True, timeout=30)
                
                results[test_file] = {
                    "success": result.returncode == 0,
                    "return_code": result.returncode,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "file_exists": os.path.exists(test_file)
                }
                
                status = "✅" if result.returncode == 0 else "❌"
                logger.info(f"{status} Error test '{test_file}': Return code {result.returncode}")
                
            except Exception as e:
                results[test_file] = {
                    "success": False,
                    "error": str(e),
                    "file_exists": os.path.exists(test_file)
                }
                logger.error(f"❌ Error test '{test_file}': {e}")
        
        return results
    
    def performance_test(self, quote_file: str, iterations: int = 10) -> Dict[str, Any]:
        """Test performance with multiple executions"""
        logger.info(f"Performance testing with {iterations} iterations...")
        
        if not os.path.exists(quote_file):
            logger.error(f"Quote file not found: {quote_file}")
            return {"error": f"Quote file not found: {quote_file}"}
        
        execution_times = []
        
        for i in range(iterations):
            start_time = time.time()
            
            try:
                result = subprocess.run([
                    self.attest_tool_path,
                    "--input", quote_file,
                    "--output-format", "json"
                ], capture_output=True, text=True, timeout=30)
                
                end_time = time.time()
                execution_time = end_time - start_time
                execution_times.append(execution_time)
                
                if i % 5 == 0:
                    logger.info(f"Iteration {i+1}/{iterations}: {execution_time:.3f}s")
                    
            except Exception as e:
                logger.error(f"Performance test iteration {i+1} failed: {e}")
                break
        
        if execution_times:
            avg_time = sum(execution_times) / len(execution_times)
            min_time = min(execution_times)
            max_time = max(execution_times)
            
            results = {
                "iterations": len(execution_times),
                "avg_execution_time": avg_time,
                "min_execution_time": min_time,
                "max_execution_time": max_time,
                "total_time": sum(execution_times),
                "execution_times": execution_times
            }
            
            logger.info(f"Performance results: avg={avg_time:.3f}s, min={min_time:.3f}s, max={max_time:.3f}s")
            return results
        
        return {"error": "No successful executions"}
    
    def run_comprehensive_analysis(self) -> Dict[str, Any]:
        """Run comprehensive analysis of attest_tool"""
        logger.info("Starting comprehensive attest_tool analysis...")
        
        analysis_results = {
            "timestamp": time.time(),
            "attest_tool_path": self.attest_tool_path,
            "basic_execution": self.test_basic_execution(),
        }
        
        # Only continue if basic execution works
        if any(test["success"] for test in analysis_results["basic_execution"].values()):
            logger.info("Basic execution successful, continuing with detailed tests...")
            
            quote_file = "../sample_data/known_good_quote.hex"
            
            analysis_results.update({
                "input_formats": self.test_input_formats(quote_file),
                "output_formats": self.test_output_formats(quote_file),
                "error_scenarios": self.test_error_scenarios(),
                "performance": self.performance_test(quote_file, iterations=5)
            })
        else:
            logger.error("Basic execution failed, skipping detailed tests")
        
        return analysis_results


def save_results(results: Dict[str, Any], output_file: str):
    """Save analysis results to JSON file"""
    try:
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        logger.info(f"Results saved to {output_file}")
    except Exception as e:
        logger.error(f"Failed to save results: {e}")


def main():
    """Main analysis function"""
    logger.info("Starting attest_tool analysis...")
    
    # Check if attest_tool exists
    attest_tool_path = "./tools/attest_tool"
    if not os.path.exists(attest_tool_path):
        logger.error(f"attest_tool not found at {attest_tool_path}")
        logger.info("Please ensure attest_tool is installed in the tools/ directory")
        return 1
    
    # Run analysis
    analyzer = AttestToolAnalyzer(attest_tool_path)
    results = analyzer.run_comprehensive_analysis()
    
    # Save results
    output_file = "../findings/attest_tool_analysis.json"
    save_results(results, output_file)
    
    # Print summary
    logger.info("Analysis complete!")
    logger.info(f"Results saved to: {output_file}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
