# MCP Protocol Overview

**Source**: https://modelcontextprotocol.io/introduction  
**Protocol Revision**: 2024-11-05

## What is MCP?

MCP (Model Context Protocol) is an open protocol that standardizes how applications provide context to LLMs. Think of MCP like a **USB-C port for AI applications** - just as USB-C provides a standardized way to connect devices to peripherals, MCP provides a standardized way to connect AI models to different data sources and tools.

## Core Value Proposition

MCP helps build agents and complex workflows on top of LLMs by providing:

- **Growing list of pre-built integrations** that LLMs can directly plug into
- **Flexibility to switch between LLM providers** and vendors
- **Best practices for securing data** within your infrastructure
- **Standardized interface** for tool and data access

## General Architecture

MCP follows a **client-server architecture** where a host application can connect to multiple servers:

```
┌─────────────────────────────────────────────────────────────┐
│                    MCP Architecture                         │
│                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │   MCP Host  │    │   MCP Host  │    │   MCP Host  │     │
│  │ (Claude     │    │ (secretGPT) │    │  (VS Code)  │     │
│  │  Desktop)   │    │             │    │             │     │
│  └──────┬──────┘    └──────┬──────┘    └──────┬──────┘     │
│         │                  │                  │            │
│  ┌──────▼──────┐    ┌──────▼──────┐    ┌──────▼──────┐     │
│  │ MCP Client  │    │ MCP Client  │    │ MCP Client  │     │
│  │    (1:1)    │    │    (1:1)    │    │    (1:1)    │     │
│  └──────┬──────┘    └──────┬──────┘    └──────┬──────┘     │
│         │                  │                  │            │
│         └─────────┬────────┴─────────┬────────┘            │
│                   │                  │                     │
│            ┌──────▼──────┐    ┌──────▼──────┐              │
│            │ MCP Server  │    │ MCP Server  │              │
│            │ (File Sys)  │    │ (Database)  │              │
│            └──────┬──────┘    └──────┬──────┘              │
│                   │                  │                     │
│         ┌─────────▼─────────┐  ┌─────▼─────────┐           │
│         │ Local Data       │  │ Remote        │           │
│         │ Sources          │  │ Services      │           │
│         └──────────────────┘  └───────────────┘           │
└─────────────────────────────────────────────────────────────┘
```

### Components

- **MCP Hosts**: Programs like Claude Desktop, IDEs, or AI tools (secretGPT) that want to access data through MCP
- **MCP Clients**: Protocol clients that maintain 1:1 connections with servers
- **MCP Servers**: Lightweight programs that expose specific capabilities through the standardized protocol
- **Local Data Sources**: Computer files, databases, and services that MCP servers can securely access
- **Remote Services**: External systems available over the internet (APIs) that MCP servers can connect to

## Key Principles

### Standardization
- **Consistent Interface**: All MCP servers expose the same protocol interface
- **Transport Agnostic**: Works over stdio, HTTP+SSE, WebSocket
- **JSON-RPC 2.0**: Standard message format for all communication

### Security First
- **User Consent**: All operations require explicit user approval
- **Access Control**: Granular permissions for different capabilities
- **Secure Transport**: Encrypted communication when needed
- **Input Validation**: All parameters validated against schemas

### Flexibility
- **Multiple Transports**: Choose appropriate communication method
- **Extensible**: Custom servers for domain-specific needs
- **Provider Agnostic**: Works with any LLM provider
- **Modular**: Connect only the servers you need

## Protocol Fundamentals

### Message Types
1. **Requests**: Expect a response (have ID)
2. **Responses**: Reply to requests (same ID)  
3. **Notifications**: One-way messages (no ID)

### Communication Pattern
- **JSON-RPC 2.0**: All messages follow this standard
- **Bidirectional**: Both client and server can initiate requests
- **Asynchronous**: Non-blocking request/response pattern

### Connection Lifecycle
1. **Initialization**: Capability negotiation
2. **Operation**: Normal message exchange
3. **Shutdown**: Graceful termination

## Integration with secretGPT

### How secretGPT Uses MCP

```
AttestAI Web UI → Hub Router → MCP Service → MCP Servers
                            ↓
                      Secret AI Service → Secret Network
```

### Benefits for secretGPT
- **Enhanced Capabilities**: Access to file systems, databases, APIs
- **Attestable Operations**: MCP tool usage included in TEE proofs
- **User Control**: Explicit approval for all tool operations
- **Extensibility**: Easy addition of new capabilities via MCP servers

### secretGPT as MCP Host
- **Hub Integration**: MCP becomes another service component
- **Security Preservation**: All MCP operations maintain TEE guarantees
- **User Experience**: Seamless tool integration in chat interface
- **Proof Generation**: MCP operations included in attestation proofs

## Use Cases for secretGPT

### Immediate Applications
- **File System Access**: Read/write files securely within TEE
- **Secret Network Tools**: Query blockchain, submit transactions
- **API Integrations**: External service calls with attestation
- **Database Queries**: Secure data access and manipulation

### Advanced Applications
- **Workflow Automation**: Multi-step tool orchestration
- **Data Analysis**: Processing and visualization tools
- **External Verification**: Third-party attestation services
- **Custom Business Logic**: Domain-specific tool development

## Next Steps

1. **Study Core Architecture** → [mcp-architecture-components.md](./mcp-architecture-components.md)
2. **Understand Primitives** → [../primitives/](../primitives/)
3. **Review Integration Patterns** → [../integration/](../integration/)
4. **Explore Security Model** → [../security/](../security/)

---

**Key Takeaway**: MCP provides the standardized interface secretGPT needs to safely and securely extend AI capabilities while maintaining TEE security guarantees and user control.
