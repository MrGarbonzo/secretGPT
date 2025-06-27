# Research Methodology for `attest_tool` Integration

## 🔬 **Research Approach**

### **Step 1: Tool Acquisition & Setup**

**Objective**: Get `attest_tool` binary and understand its basic operation

**Tasks**:
1. **Clone secret-vm-ops repository**
   ```bash
   cd F:/coding/secretGPT/experiments/attest_tool_research/
   git clone https://github.com/scrtlabs/secret-vm-ops.git
   cd secret-vm-ops
   find . -name "*attest*" -type f
   ```

2. **Locate attest_tool binary**
   - Check for compiled binaries
   - Look for source code if binary not available
   - Check for build instructions

3. **Initial execution test**
   ```bash
   ./attest_tool --help
   ./attest_tool --version
   ```

**Expected Outputs**:
- Binary location and permissions
- Command-line help documentation
- Version information

---

### **Step 2: Interface Analysis**

**Objective**: Completely understand the tool's command-line interface

**Testing Matrix**:
```bash
# Help and version
./attest_tool --help
./attest_tool -h
./attest_tool --version
./attest_tool -v

# Input format testing
./attest_tool --input quote.hex
./attest_tool -i quote.hex
./attest_tool < quote.hex
echo "040002008100..." | ./attest_tool

# Output format testing
./attest_tool --output-format json
./attest_tool --output-format text
./attest_tool --output-format raw
./attest_tool -o json

# File I/O testing
./attest_tool --input quote.hex --output result.json
./attest_tool -i quote.hex -o result.json
```

**Documentation Template**:
```markdown
## attest_tool Interface Analysis

### Command-line Arguments
- `--input, -i`: [description]
- `--output, -o`: [description]
- `--format, -f`: [description]

### Input Formats
- [Format 1]: [description]
- [Format 2]: [description]

### Output Formats  
- [Format 1]: [description]
- [Format 2]: [description]

### Return Codes
- 0: [success condition]
- 1: [error condition]
- 2: [error condition]
```

---

### **Step 3: Data Preparation**

**Objective**: Prepare test data for comprehensive validation

**Copy existing attestation data**:
```bash
# Copy known good attestation quote
cp ../../../resources/attest_data/secretAI_svm-attest.txt sample_data/known_good_quote.hex

# Create test variations
head -c 1000 sample_data/known_good_quote.hex > sample_data/truncated_quote.hex
echo "invalid_hex_data" > sample_data/invalid_quote.hex
echo "" > sample_data/empty_quote.hex
```

**Create data manifest**:
```json
{
  "test_data": {
    "known_good_quote.hex": {
      "source": "secretAI production",
      "expected_valid": true,
      "description": "Working attestation from secretAI VM"
    },
    "truncated_quote.hex": {
      "source": "derived from known_good",
      "expected_valid": false,
      "description": "Truncated quote for error testing"
    }
  }
}
```

---

### **Step 4: Output Structure Analysis**

**Objective**: Document the exact output format and fields

**Test Execution**:
```bash
# Test with known good data
./attest_tool --input sample_data/known_good_quote.hex --output-format json > sample_data/attest_tool_output.json

# Test with various formats
./attest_tool --input sample_data/known_good_quote.hex --output-format text > sample_data/attest_tool_output.txt
./attest_tool --input sample_data/known_good_quote.hex --output-format raw > sample_data/attest_tool_output.raw
```

**Analysis Template**:
```markdown
## Output Structure Analysis

### JSON Format
```json
{
  "mrtd": "...",
  "rtmr0": "...",
  "rtmr1": "...",
  // Document all fields
}
```

### Field Mapping
| attest_tool field | Current secretGPT field | Notes |
|-------------------|-------------------------|--------|
| mrtd             | mrtd                   | Direct mapping |
| rtmr0            | rtmr0                  | Direct mapping |

### Comparison with Current Parsing
| Field | Current Value | attest_tool Value | Match? |
|-------|---------------|-------------------|--------|
| mrtd  | abc123...     | abc123...        | ✅     |
```

---

### **Step 5: Validation Testing**

**Objective**: Verify accuracy and identify edge cases

**Create validation script**:
```python
# quote_analyzer.py
import subprocess
import json
import sys

def test_attest_tool(quote_file):
    """Test attest_tool with a specific quote file"""
    try:
        result = subprocess.run([
            './tools/attest_tool', 
            '--input', quote_file,
            '--output-format', 'json'
        ], capture_output=True, text=True, timeout=30)
        
        return {
            'success': result.returncode == 0,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'return_code': result.returncode
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def compare_with_current_parsing(quote_hex):
    """Compare attest_tool output with current parsing"""
    # Import current parsing logic
    from current_parser import parse_quote_hardcoded
    
    current_result = parse_quote_hardcoded(quote_hex)
    attest_tool_result = test_attest_tool_with_hex(quote_hex)
    
    return {
        'current': current_result,
        'attest_tool': attest_tool_result,
        'matches': compare_results(current_result, attest_tool_result)
    }
```

**Testing scenarios**:
1. Known good quotes
2. Malformed quotes
3. Empty input
4. Large quotes
5. Network-sourced quotes

---

### **Step 6: Performance Analysis**

**Objective**: Measure execution time and resource usage

**Create performance test**:
```python
# performance_test.py
import time
import subprocess
import psutil
import statistics

def benchmark_attest_tool(quote_file, iterations=100):
    """Benchmark attest_tool performance"""
    execution_times = []
    memory_usage = []
    
    for i in range(iterations):
        start_time = time.time()
        process = subprocess.Popen([
            './tools/attest_tool',
            '--input', quote_file,
            '--output-format', 'json'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Monitor memory usage
        try:
            psutil_process = psutil.Process(process.pid)
            memory_usage.append(psutil_process.memory_info().rss)
        except:
            pass
            
        stdout, stderr = process.communicate()
        end_time = time.time()
        
        execution_times.append(end_time - start_time)
    
    return {
        'avg_execution_time': statistics.mean(execution_times),
        'min_execution_time': min(execution_times),
        'max_execution_time': max(execution_times),
        'std_execution_time': statistics.stdev(execution_times),
        'avg_memory_usage': statistics.mean(memory_usage) if memory_usage else None
    }
```

---

### **Step 7: Integration Design**

**Objective**: Design the integration pattern for secretGPT

**Create integration prototype**:
```python
# subprocess_wrapper.py
import asyncio
import subprocess
import tempfile
import json
import logging
from typing import Dict, Any, Optional

class AttestToolWrapper:
    """Async wrapper for attest_tool integration"""
    
    def __init__(self, attest_tool_path: str, timeout: int = 30):
        self.attest_tool_path = attest_tool_path
        self.timeout = timeout
        self.logger = logging.getLogger(__name__)
    
    async def parse_attestation_quote(self, quote_hex: str) -> Dict[str, Any]:
        """Parse attestation quote using attest_tool"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.hex', delete=False) as f:
            f.write(quote_hex)
            quote_file = f.name
        
        try:
            # Execute attest_tool asynchronously
            process = await asyncio.create_subprocess_exec(
                self.attest_tool_path,
                '--input', quote_file,
                '--output-format', 'json',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(), 
                timeout=self.timeout
            )
            
            if process.returncode != 0:
                raise AttestToolError(f"attest_tool failed: {stderr.decode()}")
            
            return json.loads(stdout.decode())
            
        except asyncio.TimeoutError:
            raise AttestToolError(f"attest_tool timed out after {self.timeout}s")
        finally:
            # Cleanup temp file
            try:
                os.unlink(quote_file)
            except:
                pass

class AttestToolError(Exception):
    """Custom exception for attest_tool errors"""
    pass
```

---

## 📋 **Research Checklist**

### **Phase 1: Setup** ⏳
- [ ] Clone secret-vm-ops repository
- [ ] Locate attest_tool binary
- [ ] Test basic execution
- [ ] Document installation requirements

### **Phase 2: Interface** ⏳
- [ ] Document all command-line arguments
- [ ] Test input format variations
- [ ] Test output format options
- [ ] Document return codes and errors

### **Phase 3: Data Preparation** ⏳
- [ ] Copy existing attestation quotes
- [ ] Create test variations (malformed, empty, etc.)
- [ ] Create data manifest
- [ ] Verify data integrity

### **Phase 4: Output Analysis** ⏳
- [ ] Document JSON output structure
- [ ] Map fields to current secretGPT fields
- [ ] Compare output with current parsing
- [ ] Document any discrepancies

### **Phase 5: Validation** ⏳
- [ ] Test with known good quotes
- [ ] Test error scenarios
- [ ] Create validation script
- [ ] Document edge cases

### **Phase 6: Performance** ⏳
- [ ] Benchmark execution time
- [ ] Monitor memory usage
- [ ] Test with concurrent executions
- [ ] Document performance characteristics

### **Phase 7: Integration** ⏳
- [ ] Design async wrapper
- [ ] Implement error handling
- [ ] Create fallback strategy
- [ ] Test integration prototype

---

## 🎯 **Success Metrics**

- **Documentation Complete**: All interface aspects documented
- **Validation Passed**: Output matches current parsing for known data
- **Performance Acceptable**: Execution time < 5 seconds per quote
- **Error Handling**: Graceful handling of all error scenarios
- **Integration Ready**: Working prototype that can be tested in secretGPT

---

**Next**: Begin with Step 1 - Tool Acquisition & Setup
