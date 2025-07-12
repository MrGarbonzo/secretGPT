# MCP Resources Concept

**Source**: https://modelcontextprotocol.io/docs/concepts/resources  
**Protocol Revision**: 2024-11-05

## Overview

Resources are a core primitive in the Model Context Protocol (MCP) that allow servers to expose data and content that can be read by clients and used as context for LLM interactions.

**Key Principle**: Resources are designed to be **application-controlled**, meaning that the client application can decide how and when they should be used.

## Control Models Comparison

### Resources vs. Tools
| Aspect | Resources | Tools |
|--------|-----------|-------|
| **Control** | Application-controlled | Model-controlled |
| **Purpose** | Provide data/context | Perform actions |
| **Initiative** | Client decides when to use | AI decides when to use |
| **State** | Read-only access | Can modify state |
| **Usage Pattern** | Explicit selection | Automatic invocation |

### Different Client Behaviors

Different MCP clients may handle resources differently:

- **Claude Desktop**: Requires users to explicitly select resources before use
- **Other clients**: Might automatically select resources based on heuristics  
- **Advanced implementations**: May allow AI model to determine which resources to use
- **secretGPT**: Should provide user control with optional AI recommendations

## Resource Types and Content

### Resource URIs

Resources are identified using URIs that follow this format:

```
protocol://path/to/resource
```

**Examples:**
```
file:///home/user/documents/report.pdf
postgres://database/customers/schema
screen://localhost/display1
secret://mainnet/contract/secret1abc123/state
```

**Key Points:**
- Protocol and path structure defined by MCP server implementation
- Servers can define their own custom URI schemes
- URIs must be unique within server scope
- Support for hierarchical and flat namespace models

### Content Types

#### Text Resources
Contains UTF-8 encoded text data, suitable for:
- **Source code** and configuration files
- **Log files** and system outputs
- **JSON/XML data** and structured content
- **Plain text** documents and notes
- **Markdown** documentation

```json
{
  "uri": "file:///home/user/config.json",
  "name": "Application Configuration",
  "mimeType": "application/json",
  "text": "{\"database\": \"postgresql://...\", \"debug\": true}"
}
```

#### Binary Resources  
Contains raw binary data encoded in base64, suitable for:
- **Images** and graphics files
- **PDFs** and document files
- **Audio files** and media content
- **Video files** and multimedia
- **Other non-text formats**

```json
{
  "uri": "file:///home/user/chart.png", 
  "name": "Performance Chart",
  "mimeType": "image/png",
  "blob": "iVBORw0KGgoAAAANSUhEUgAA..."
}
```

## Resource Discovery

### Direct Resources

Servers expose concrete resources via the `resources/list` endpoint:

**Request:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "resources/list"
}
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "resources": [
      {
        "uri": "file:///home/user/documents/report.pdf",
        "name": "Annual Report 2024", 
        "description": "Company annual financial report",
        "mimeType": "application/pdf",
        "size": 2048576
      },
      {
        "uri": "secret://mainnet/contract/secret1abc123",
        "name": "Smart Contract State",
        "description": "Current state of the privacy contract",
        "mimeType": "application/json"
      }
    ]
  }
}
```

### Resource Templates

For dynamic resources, servers can expose URI templates following RFC 6570:

**Template Definition:**
```json
{
  "uriTemplate": "file:///logs/{date}/{level}.log",
  "name": "Application Logs",
  "description": "Daily application logs by level",
  "mimeType": "text/plain"
}
```

**Template Usage:**
```
file:///logs/2024-12-20/error.log
file:///logs/2024-12-20/info.log
file:///logs/2024-12-19/debug.log
```

## Resource Reading

### Basic Read Operation

**Request:**
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "resources/read",
  "params": {
    "uri": "file:///home/user/documents/report.pdf"
  }
}
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "contents": [
      {
        "uri": "file:///home/user/documents/report.pdf",
        "mimeType": "application/pdf",
        "blob": "JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwo..."
      }
    ]
  }
}
```

### Multiple Resource Response

Servers may return multiple resources in response to one `resources/read` request:

**Use Cases:**
- **Directory listing**: Return all files in a directory
- **Batch processing**: Return related resources together
- **Hierarchical data**: Return parent and child resources

**Example Response:**
```json
{
  "contents": [
    {
      "uri": "file:///home/user/project/README.md",
      "mimeType": "text/markdown", 
      "text": "# Project Documentation\n..."
    },
    {
      "uri": "file:///home/user/project/package.json",
      "mimeType": "application/json",
      "text": "{\"name\": \"my-project\", ...}"
    }
  ]
}
```

## Real-Time Updates

### List Change Notifications

Servers can notify clients when resource lists change:

**Notification:**
```json
{
  "jsonrpc": "2.0",
  "method": "notifications/resources/list_changed"
}
```

**Client Response:** Re-fetch resource list with `resources/list`

### Resource Subscriptions

For frequently changing resources, clients can subscribe to updates:

#### 1. Subscribe to Resource
```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "resources/subscribe", 
  "params": {
    "uri": "secret://mainnet/contract/secret1abc123/state"
  }
}
```

#### 2. Receive Update Notifications
```json
{
  "jsonrpc": "2.0",
  "method": "notifications/resources/updated",
  "params": {
    "uri": "secret://mainnet/contract/secret1abc123/state"
  }
}
```

#### 3. Fetch Latest Content
```json
{
  "jsonrpc": "2.0",
  "id": 4, 
  "method": "resources/read",
  "params": {
    "uri": "secret://mainnet/contract/secret1abc123/state"
  }
}
```

#### 4. Unsubscribe When Done
```json
{
  "jsonrpc": "2.0",
  "id": 5,
  "method": "resources/unsubscribe",
  "params": {
    "uri": "secret://mainnet/contract/secret1abc123/state"
  }
}
```

## secretGPT Resource Categories

### File System Resources
```json
{
  "uri": "file:///app/data/documents/{filename}",
  "name": "TEE Document Storage",
  "description": "Secure document storage within TEE boundaries",
  "mimeType": "application/octet-stream"
}
```

### Secret Network Resources
```json
{
  "uri": "secret://mainnet/account/{address}/balance",
  "name": "Account Balance",
  "description": "SCRT balance for specified address",
  "mimeType": "application/json"
}
```

### Attestation Resources
```json
{
  "uri": "attestation://localhost/vm/current/state",
  "name": "Current VM Attestation",
  "description": "Real-time TEE attestation data",
  "mimeType": "application/json"
}
```

### Configuration Resources
```json
{
  "uri": "config://secretgpt/settings/current",
  "name": "secretGPT Configuration", 
  "description": "Current application settings and preferences",
  "mimeType": "application/json"
}
```

### Log Resources
```json
{
  "uri": "logs://secretgpt/{date}/{level}.log",
  "name": "Application Logs",
  "description": "Daily application logs by severity level",
  "mimeType": "text/plain"
}
```

## Best Practices for secretGPT

### Resource Design
1. **Clear Naming**: Use descriptive, hierarchical resource names
2. **Consistent URIs**: Follow consistent URI schemes across servers
3. **Appropriate MIME Types**: Set correct MIME types for content
4. **Size Awareness**: Include size information for large resources
5. **Documentation**: Provide helpful descriptions for resource purpose

### Security Considerations  
1. **URI Validation**: Validate all resource URIs before processing
2. **Access Controls**: Implement appropriate access controls for sensitive resources
3. **Path Sanitization**: Prevent directory traversal attacks
4. **Content Validation**: Validate MIME types and content structure
5. **Resource Limits**: Implement size limits and rate limiting

### Performance Optimization
1. **Caching**: Cache resource contents when appropriate
2. **Pagination**: Support pagination for large resource lists
3. **Incremental Updates**: Use subscriptions for frequently changing resources
4. **Lazy Loading**: Load resource content only when needed
5. **Compression**: Compress large text resources

### TEE Integration
1. **Secure Storage**: Store sensitive resources in TEE-protected storage
2. **Attestable Access**: Include resource access in attestation proofs
3. **Key Management**: Securely handle encryption keys for encrypted resources
4. **Isolation**: Isolate resource access within TEE boundaries

## Error Handling

### Common Error Scenarios

**Resource Not Found:**
```json
{
  "error": {
    "code": -32602,
    "message": "Resource not found",
    "data": {
      "uri": "file:///invalid/path",
      "reason": "File does not exist"
    }
  }
}
```

**Access Denied:**
```json
{
  "error": {
    "code": -32603,
    "message": "Access denied", 
    "data": {
      "uri": "file:///restricted/file",
      "reason": "Insufficient permissions"
    }
  }
}
```

**Invalid URI:**
```json
{
  "error": {
    "code": -32602,
    "message": "Invalid URI format",
    "data": {
      "uri": "invalid-uri",
      "reason": "URI must include protocol scheme"
    }
  }
}
```

## Integration with secretGPT Hub

### Resource Discovery Flow
```
AttestAI UI → Hub Router → MCP Service → Resource List → User Selection
                      ↓
               Selected resources → AI Context → Secret AI
```

### Hub Router Integration
1. **Resource Aggregation**: Collect resources from all connected MCP servers
2. **URI Namespacing**: Prevent URI conflicts between servers
3. **Content Caching**: Cache frequently accessed resources
4. **Access Logging**: Log all resource access for attestation

### User Experience
1. **Resource Browser**: UI for browsing available resources
2. **Search Functionality**: Search resources by name, type, or content
3. **Preview Capability**: Preview resource content before selection
4. **Bulk Selection**: Select multiple related resources efficiently

---

**Next Steps:**
- Review **[Resource Implementation Guide](../implementation/mcp-server-development.md)** for exposing resources
- Study **[Secret Network Resources](../secret-network/secret-network-mcp-resources.md)** for blockchain data
- Explore **[Security Model](../security/mcp-resource-security.md)** for safe resource access
