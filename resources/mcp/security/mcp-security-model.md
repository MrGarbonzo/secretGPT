# MCP Security Model for TEE Environments

**Reference**: MCP Security Best Practices + TEE Integration Requirements  
**Target**: secretGPT TEE Attestation + MCP Integration

## Overview

This document outlines the security model for integrating MCP (Model Context Protocol) operations within secretGPT's Trusted Execution Environment (TEE), ensuring that MCP tool execution maintains the same security guarantees as direct Secret AI interactions.

## Security Principles

### Core TEE Requirements

1. **Attestable Operations**: All MCP operations must be included in TEE attestation proofs
2. **User Consent**: Explicit user approval required for all tool executions
3. **Data Isolation**: MCP operations contained within TEE boundaries
4. **Cryptographic Integrity**: Tool results included in cryptographic verification
5. **Audit Trail**: Complete logging of all MCP activities

### MCP Security Framework

Based on MCP specification security guidelines:

- **User Consent and Control**: Users must explicitly consent to and understand all data access and operations
- **Data Privacy**: Hosts must obtain explicit user consent before exposing user data to servers
- **Access Controls**: Implement appropriate access controls and data protections
- **Input Validation**: All MCP messages and parameters must be validated
- **Transport Security**: Secure communication channels for MCP operations

## Threat Model

### Attack Vectors

#### 1. Malicious MCP Servers
**Risk**: Compromised or malicious MCP servers attempting to:
- Extract sensitive data from TEE
- Execute unauthorized operations
- Poison tool results to influence AI responses

**Mitigation**:
- Server allowlisting and approval process
- Capability-based access controls
- Result validation and sanitization
- Network isolation for external servers

#### 2. Tool Parameter Injection
**Risk**: Malicious parameters in tool calls attempting:
- Command injection in system tools
- Path traversal in file system tools
- SQL injection in database tools

**Mitigation**:
- Comprehensive input validation using JSON Schema
- Parameter sanitization and escaping
- Principle of least privilege for tool execution
- Sandboxed execution environments

#### 3. Data Exfiltration
**Risk**: MCP tools attempting to:
- Access data outside authorized scope
- Transmit sensitive data to external systems
- Bypass TEE data protection

**Mitigation**:
- Resource access controls and validation
- Network egress monitoring and filtering
- Data flow tracking and logging
- Encryption of sensitive data at rest and in transit

#### 4. TEE Bypass Attempts
**Risk**: MCP operations attempting to:
- Escape TEE execution environment
- Access host system resources
- Compromise attestation integrity

**Mitigation**:
- Strict TEE boundary enforcement
- Regular attestation validation
- Runtime integrity monitoring
- Isolated execution contexts

## Authentication and Authorization

### MCP Server Authentication

```python
class SecureMCPConnection:
    """Secure MCP connection with TEE integration"""
    
    def __init__(self, server_config, tee_context):
        self.server_config = server_config
        self.tee_context = tee_context
        self.authenticated = False
        self.capabilities = {}
    
    async def authenticate(self):
        """Authenticate MCP server within TEE context"""
        
        # 1. Verify server certificate/signature
        if not await self._verify_server_identity():
            raise AuthenticationError("Server identity verification failed")
        
        # 2. Perform TEE-aware handshake
        attestation_challenge = await self._generate_attestation_challenge()
        server_response = await self._send_challenge(attestation_challenge)
        
        if not await self._verify_attestation_response(server_response):
            raise AuthenticationError("Server attestation verification failed")
        
        # 3. Establish secure channel
        await self._establish_secure_channel()
        self.authenticated = True
    
    async def _verify_server_identity(self):
        """Verify server identity using certificates or signatures"""
        # Implementation specific to server type
        pass
    
    async def _generate_attestation_challenge(self):
        """Generate TEE-specific attestation challenge"""
        return {
            "challenge": self.tee_context.generate_nonce(),
            "tee_measurement": self.tee_context.get_measurement(),
            "timestamp": time.time()
        }
```

### Tool Authorization Framework

```python
class ToolAuthorizationManager:
    """Manages authorization for MCP tool execution"""
    
    def __init__(self, user_consent_manager, tee_context):
        self.user_consent_manager = user_consent_manager
        self.tee_context = tee_context
        self.tool_permissions = {}  # tool_name -> permissions
    
    async def authorize_tool_execution(self, tool_name, arguments, user_id):
        """Authorize tool execution with user consent"""
        
        # 1. Check tool permissions
        if not await self._check_tool_permissions(tool_name, user_id):
            raise AuthorizationError(f"Tool {tool_name} not authorized for user")
        
        # 2. Validate arguments against schema
        if not await self._validate_arguments(tool_name, arguments):
            raise ValidationError("Tool arguments failed validation")
        
        # 3. Get user consent for this specific execution
        consent_granted = await self.user_consent_manager.request_consent(
            user_id=user_id,
            operation="tool_execution",
            details={
                "tool_name": tool_name,
                "arguments": arguments,
                "risk_level": self._assess_risk_level(tool_name, arguments)
            }
        )
        
        if not consent_granted:
            raise AuthorizationError("User consent not granted")
        
        # 4. Log authorization decision
        await self._log_authorization(user_id, tool_name, arguments, "granted")
        
        return True
    
    def _assess_risk_level(self, tool_name, arguments):
        """Assess risk level of tool execution"""
        risk_factors = {
            "file_write": 3,      # High risk - modifies file system
            "network_request": 2,  # Medium risk - external communication
            "query_balance": 1,    # Low risk - read-only blockchain query
            "math_calculate": 0    # No risk - pure computation
        }
        
        base_risk = risk_factors.get(tool_name, 2)  # Default medium risk
        
        # Increase risk based on arguments
        if "sensitive" in str(arguments).lower():
            base_risk += 1
        
        return min(base_risk, 3)  # Cap at high risk
```

## Input Validation and Sanitization

### JSON Schema Validation

```python
class SecureToolValidator:
    """Validates MCP tool inputs within TEE context"""
    
    def __init__(self, tee_context):
        self.tee_context = tee_context
        self.schema_cache = {}
    
    async def validate_tool_call(self, tool_name, arguments, schema):
        """Comprehensive validation of tool call parameters"""
        
        # 1. Schema validation
        try:
            jsonschema.validate(arguments, schema)
        except jsonschema.ValidationError as e:
            raise ValidationError(f"Schema validation failed: {e.message}")
        
        # 2. TEE-specific validation
        await self._validate_tee_constraints(tool_name, arguments)
        
        # 3. Security-specific validation
        await self._validate_security_constraints(tool_name, arguments)
        
        return True
    
    async def _validate_tee_constraints(self, tool_name, arguments):
        """Validate arguments against TEE-specific constraints"""
        
        # File path validation
        if "path" in arguments or "filepath" in arguments:
            path = arguments.get("path") or arguments.get("filepath")
            if not self._is_path_within_tee(path):
                raise ValidationError(f"Path {path} outside TEE boundaries")
        
        # Network access validation
        if "url" in arguments:
            url = arguments.get("url")
            if not self._is_url_allowed(url):
                raise ValidationError(f"URL {url} not in allowlist")
    
    def _is_path_within_tee(self, path):
        """Verify path is within TEE-allowed directories"""
        allowed_paths = ["/app/data", "/tmp/secretgpt"]
        normalized_path = os.path.normpath(path)
        
        return any(
            normalized_path.startswith(allowed) 
            for allowed in allowed_paths
        )
    
    def _is_url_allowed(self, url):
        """Verify URL is in allowlist for external access"""
        allowed_domains = [
            "api.secretnetwork.io",
            "faucet.secretnetwork.io", 
            "explorer.secretnetwork.io"
        ]
        
        parsed_url = urllib.parse.urlparse(url)
        return parsed_url.hostname in allowed_domains
```

### Parameter Sanitization

```python
class ParameterSanitizer:
    """Sanitizes tool parameters to prevent injection attacks"""
    
    @staticmethod
    def sanitize_file_path(path):
        """Sanitize file path to prevent directory traversal"""
        # Remove dangerous sequences
        dangerous_patterns = ["../", "..\\", "..", "~", "/etc", "/proc"]
        sanitized = path
        
        for pattern in dangerous_patterns:
            sanitized = sanitized.replace(pattern, "")
        
        # Normalize and validate
        sanitized = os.path.normpath(sanitized)
        
        if not sanitized.startswith("/app/"):
            raise ValidationError("Path must be within /app/ directory")
        
        return sanitized
    
    @staticmethod
    def sanitize_command_arguments(args):
        """Sanitize command arguments to prevent command injection"""
        if isinstance(args, str):
            # Remove shell metacharacters
            dangerous_chars = [";", "&", "|", "`", "$", "(", ")", "<", ">"]
            sanitized = args
            
            for char in dangerous_chars:
                sanitized = sanitized.replace(char, "")
            
            return sanitized
        
        elif isinstance(args, list):
            return [ParameterSanitizer.sanitize_command_arguments(arg) for arg in args]
        
        return args
```

## Secure Tool Execution

### Sandboxed Execution Environment

```python
class TEEToolExecutor:
    """Executes MCP tools within secure TEE sandbox"""
    
    def __init__(self, tee_context, attestation_service):
        self.tee_context = tee_context
        self.attestation_service = attestation_service
        self.execution_log = []
    
    async def execute_tool_securely(self, tool_name, arguments, server_connection):
        """Execute tool with full TEE security guarantees"""
        
        # 1. Create execution context
        execution_id = self._generate_execution_id()
        execution_context = {
            "execution_id": execution_id,
            "tool_name": tool_name,
            "arguments": arguments,
            "timestamp": time.time(),
            "tee_measurement": self.tee_context.get_current_measurement()
        }
        
        try:
            # 2. Pre-execution validation
            await self._pre_execution_checks(execution_context)
            
            # 3. Execute with resource monitoring
            result = await self._execute_with_monitoring(
                tool_name, arguments, server_connection, execution_context
            )
            
            # 4. Post-execution validation
            validated_result = await self._post_execution_validation(result, execution_context)
            
            # 5. Log successful execution
            await self._log_execution_success(execution_context, validated_result)
            
            return validated_result
            
        except Exception as e:
            # 6. Log execution failure
            await self._log_execution_failure(execution_context, e)
            raise
    
    async def _execute_with_monitoring(self, tool_name, arguments, server_connection, context):
        """Execute tool with resource monitoring and timeouts"""
        
        # Set execution limits
        timeout = 30  # 30 second timeout
        max_memory = 100 * 1024 * 1024  # 100MB memory limit
        
        # Monitor resource usage during execution
        with ResourceMonitor(max_memory=max_memory) as monitor:
            try:
                # Execute with timeout
                result = await asyncio.wait_for(
                    server_connection.call_tool(tool_name, arguments),
                    timeout=timeout
                )
                
                # Include resource usage in context
                context["resource_usage"] = monitor.get_usage()
                
                return result
                
            except asyncio.TimeoutError:
                raise ToolExecutionError(f"Tool {tool_name} execution timed out")
            except MemoryError:
                raise ToolExecutionError(f"Tool {tool_name} exceeded memory limit")
    
    async def _post_execution_validation(self, result, context):
        """Validate tool execution result"""
        
        # 1. Validate result structure
        if not isinstance(result, dict) or "content" not in result:
            raise ValidationError("Invalid tool result structure")
        
        # 2. Scan for sensitive data leakage
        if self._contains_sensitive_data(result):
            raise SecurityError("Tool result contains sensitive data")
        
        # 3. Validate result size
        result_size = len(json.dumps(result))
        if result_size > 1024 * 1024:  # 1MB limit
            raise ValidationError("Tool result exceeds size limit")
        
        # 4. Add TEE attestation to result
        result["tee_attestation"] = {
            "execution_id": context["execution_id"],
            "measurement": context["tee_measurement"],
            "timestamp": context["timestamp"]
        }
        
        return result
```

## Attestation Integration

### MCP Operations in TEE Proofs

```python
class MCPAttestationIntegrator:
    """Integrates MCP operations into TEE attestation proofs"""
    
    def __init__(self, attestation_service):
        self.attestation_service = attestation_service
        self.mcp_operations = []
    
    def record_mcp_operation(self, operation_type, details):
        """Record MCP operation for attestation inclusion"""
        
        operation_record = {
            "operation_type": operation_type,  # "tool_execution", "resource_read"
            "details": details,
            "timestamp": time.time(),
            "tee_measurement": self.attestation_service.get_current_measurement(),
            "operation_hash": self._hash_operation(operation_type, details)
        }
        
        self.mcp_operations.append(operation_record)
    
    async def generate_mcp_attestation_proof(self, conversation_data):
        """Generate attestation proof including MCP operations"""
        
        # 1. Get standard TEE attestation
        tee_attestation = await self.attestation_service.get_self_attestation()
        
        # 2. Include MCP operations
        enhanced_attestation = {
            **tee_attestation,
            "mcp_operations": self.mcp_operations,
            "mcp_summary": {
                "total_operations": len(self.mcp_operations),
                "operation_types": list(set(op["operation_type"] for op in self.mcp_operations)),
                "tools_used": list(set(
                    op["details"].get("tool_name") 
                    for op in self.mcp_operations 
                    if op["operation_type"] == "tool_execution"
                ))
            }
        }
        
        # 3. Generate cryptographic proof
        proof_data = {
            "conversation": conversation_data,
            "attestation": enhanced_attestation,
            "proof_timestamp": time.time()
        }
        
        return await self._sign_attestation_proof(proof_data)
    
    def _hash_operation(self, operation_type, details):
        """Generate hash of MCP operation for integrity verification"""
        operation_string = json.dumps({
            "type": operation_type,
            "details": details
        }, sort_keys=True)
        
        return hashlib.sha256(operation_string.encode()).hexdigest()
```

## Network Security

### Secure MCP Transport

```python
class SecureMCPTransport:
    """Secure transport layer for MCP communications"""
    
    def __init__(self, tee_context):
        self.tee_context = tee_context
        self.connection_pool = {}
    
    async def create_secure_connection(self, server_config):
        """Create secure connection to MCP server"""
        
        if server_config.transport == "stdio":
            # Local stdio connection within TEE
            return await self._create_stdio_connection(server_config)
        
        elif server_config.transport == "sse":
            # HTTP+SSE with TLS
            return await self._create_https_sse_connection(server_config)
        
        elif server_config.transport == "websocket":
            # WebSocket with TLS
            return await self._create_wss_connection(server_config)
        
        else:
            raise UnsupportedTransportError(f"Transport {server_config.transport} not supported")
    
    async def _create_https_sse_connection(self, server_config):
        """Create HTTPS+SSE connection with certificate validation"""
        
        # Configure TLS context
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = True
        ssl_context.verify_mode = ssl.CERT_REQUIRED
        
        # Add TEE-specific certificate validation
        ssl_context.set_verify_flags(ssl.VERIFY_X509_STRICT)
        
        # Create connection with security headers
        headers = {
            "User-Agent": "secretGPT-TEE/1.0",
            "X-TEE-Measurement": self.tee_context.get_measurement(),
            "Authorization": f"Bearer {server_config.api_key}"
        }
        
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        session = aiohttp.ClientSession(
            connector=connector,
            headers=headers,
            timeout=aiohttp.ClientTimeout(total=30)
        )
        
        return session
```

## Monitoring and Auditing

### Security Event Logging

```python
class MCPSecurityLogger:
    """Logs security-relevant MCP events for audit trail"""
    
    def __init__(self, tee_context):
        self.tee_context = tee_context
        self.security_events = []
    
    def log_security_event(self, event_type, details, severity="INFO"):
        """Log security event with TEE context"""
        
        event = {
            "event_type": event_type,
            "details": details,
            "severity": severity,
            "timestamp": time.time(),
            "tee_measurement": self.tee_context.get_measurement(),
            "event_hash": self._hash_event(event_type, details)
        }
        
        self.security_events.append(event)
        
        # Log to system log as well
        logger.log(
            getattr(logging, severity),
            f"MCP Security Event: {event_type} - {details}"
        )
    
    def log_tool_execution(self, tool_name, arguments, result, user_id):
        """Log tool execution for audit trail"""
        self.log_security_event(
            "tool_execution",
            {
                "tool_name": tool_name,
                "arguments_hash": self._hash_data(arguments),
                "result_hash": self._hash_data(result),
                "user_id": user_id
            }
        )
    
    def log_authorization_decision(self, user_id, resource, decision, reason):
        """Log authorization decisions"""
        self.log_security_event(
            "authorization_decision",
            {
                "user_id": user_id,
                "resource": resource,
                "decision": decision,
                "reason": reason
            }
        )
    
    def get_audit_trail(self):
        """Get complete audit trail for attestation inclusion"""
        return {
            "security_events": self.security_events,
            "event_count": len(self.security_events),
            "audit_hash": self._hash_audit_trail()
        }
```

## Best Practices Summary

### Implementation Guidelines

1. **Defense in Depth**: Multiple layers of security validation
2. **Principle of Least Privilege**: Minimal permissions for all operations
3. **Fail Secure**: Default to denial when security checks fail
4. **Complete Audit Trail**: Log all security-relevant events
5. **User Transparency**: Clear indication of all MCP operations

### Security Checklist

- [ ] MCP server authentication and authorization implemented
- [ ] Tool parameter validation and sanitization in place
- [ ] Resource access controls configured
- [ ] TEE boundary enforcement verified
- [ ] Attestation integration tested
- [ ] Security event logging enabled
- [ ] User consent mechanisms implemented
- [ ] Network security configured (TLS, certificate validation)
- [ ] Input/output validation comprehensive
- [ ] Error handling secure (no information leakage)

---

**Next Steps:**
- Review **[Tool Sandboxing](./mcp-tool-sandboxing.md)** for detailed execution security
- Study **[Attestation Integration](../integration/mcp-attestation-integration.md)** for TEE proof generation
- Explore **[Implementation Guide](../implementation/mcp-server-development.md)** for secure server development
