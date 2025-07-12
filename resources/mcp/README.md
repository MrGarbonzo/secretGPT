# Model Context Protocol (MCP) Reference Library

This directory contains comprehensive reference documentation for integrating the Model Context Protocol (MCP) into secretGPT. The documentation is organized by functional areas to support development and implementation.

## 📚 Library Structure

### Core Protocol Understanding
- **[core/](./core/)** - Fundamental MCP concepts, architecture, and protocol basics

### Server Primitives
- **[primitives/](./primitives/)** - Resources, Tools, Prompts, and Sampling concepts

### Integration Patterns
- **[integration/](./integration/)** - How to integrate MCP with secretGPT's hub architecture

### Secret Network Integration
- **[secret-network/](./secret-network/)** - Blockchain-specific MCP tools and patterns

### Security & Best Practices
- **[security/](./security/)** - Security considerations for MCP in TEE environments

### Implementation Guides
- **[implementation/](./implementation/)** - Practical development guidance

### Transport & Communication
- **[transport/](./transport/)** - Message transport mechanisms and patterns

### Ecosystem & Examples
- **[ecosystem/](./ecosystem/)** - Available servers, tools, and implementation examples

## 🎯 Quick Reference

### Key MCP Concepts
- **MCP is like "USB-C for AI"** - standardizes how applications connect to data sources and tools
- **Client-Server Architecture** - secretGPT acts as MCP client, connects to MCP servers
- **JSON-RPC 2.0 Messaging** - all communication uses standard JSON-RPC protocol
- **Three Primitives**: Resources (data), Tools (actions), Prompts (templates)

### Integration with secretGPT
- MCP integrates as a new service component in the hub router
- Follows same patterns as existing Secret AI service integration
- Maintains TEE attestation guarantees for all MCP operations
- Supports both AttestAI testing and future secretGPT frontend

### Security Model
- **User Consent**: All MCP operations require explicit user approval
- **TEE Integration**: MCP tool execution included in attestation proofs
- **Input Validation**: All tool parameters validated against JSON schemas
- **Access Control**: Granular permissions for different tool categories

## 🚀 Implementation Roadmap

### Phase 1: Basic MCP Integration
1. Add MCP service to hub router (`ComponentType.MCP_SERVICE`)
2. Implement basic tool discovery and execution
3. Test with simple tools (file system, basic APIs)
4. Validate attestation inclusion

### Phase 2: Secret Network Tools
1. Develop Secret Network query tools
2. Implement transaction submission tools
3. Add governance and staking tools
4. Optimize for blockchain performance

### Phase 3: Advanced Features
1. Tool chaining and composition
2. Resource subscriptions and real-time updates
3. Prompt template system
4. Sampling integration (when supported)

## 📖 Documentation Sources

This reference library is based on:
- **Official MCP Documentation**: https://modelcontextprotocol.io/
- **MCP Specification**: https://spec.modelcontextprotocol.io/
- **Protocol Revision**: 2024-11-05 (current as of documentation creation)
- **TypeScript Schema**: Source of truth for all protocol messages

## 🔗 Related secretGPT Documentation

- **[../secretAI/](../secretAI/)** - Secret AI SDK integration patterns
- **[../attest_data/](../attest_data/)** - Attestation reference data
- **[../scripts/](../scripts/)** - Environment setup and validation scripts

## 📝 Notes for Developers

- **Start with AttestAI**: Use existing web UI for MCP testing and validation
- **Follow Hub Patterns**: MCP integration should mirror Secret AI service patterns
- **Maintain Security**: All MCP operations must preserve TEE guarantees
- **Document Everything**: Track which tools work, performance characteristics, security implications

---

**Last Updated**: Based on MCP documentation as of December 2024
**Target Integration**: secretGPT Phase 1 MCP Implementation
