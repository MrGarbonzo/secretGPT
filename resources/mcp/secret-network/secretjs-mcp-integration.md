# SecretJS MCP Integration

**Purpose**: Using SecretJS library within MCP tools for Secret Network interactions  
**Reference**: SecretJS Documentation, Secret Network client patterns  
**Integration**: MCP tools leveraging SecretJS for blockchain queries

## Overview

This document outlines how to integrate SecretJS (the official Secret Network JavaScript/TypeScript client library) within MCP tools to provide robust, type-safe interactions with Secret Network blockchain.

## SecretJS vs Direct REST API

### When to Use SecretJS
- **Type Safety**: Built-in TypeScript types for all operations
- **Connection Management**: Automatic retry logic and connection pooling  
- **Data Formatting**: Automatic unit conversions (uscrt ↔ SCRT)
- **Error Handling**: Standardized error responses
- **Future Compatibility**: Easier migration to transaction tools (Phase 2)

### When to Use Direct REST
- **Minimal Dependencies**: Smaller bundle size for simple queries
- **Custom Endpoints**: Using non-standard API endpoints
- **Performance**: Direct HTTP requests for high-frequency operations

## SecretJS Installation and Setup

### Dependencies

```json
{
  "dependencies": {
    "secretjs": "^1.12.0",
    "@types/node": "^18.0.0"
  }
}
```

### Basic Client Setup

```typescript
import { SecretNetworkClient } from 'secretjs';

class SecretJSMCPProvider {
    private queryClient: SecretNetworkClient;
    private signingClient?: SecretNetworkClient;
    
    constructor(network: 'mainnet' | 'testnet' = 'mainnet') {
        this.initializeClient(network);
    }
    
    private async initializeClient(network: string) {
        // Network configuration
        const config = this.getNetworkConfig(network);
        
        // Query-only client (no wallet required)
        this.queryClient = new SecretNetworkClient({
            url: config.lcdUrl,
            chainId: config.chainId,
        });
        
        // For Phase 2: Signing client with Keplr
        // this.signingClient = await this.setupSigningClient(config);
    }
    
    private getNetworkConfig(network: string) {
        const configs = {
            mainnet: {
                chainId: 'secret-4',
                lcdUrl: 'https://lcd.mainnet.secretsaturn.net',
                rpcUrl: 'https://rpc.mainnet.secretsaturn.net'
            },
            testnet: {
                chainId: 'pulsar-3', 
                lcdUrl: 'https://lcd.testnet.secretsaturn.net',
                rpcUrl: 'https://rpc.testnet.secretsaturn.net'
            }
        };
        
        return configs[network] || configs.mainnet;
    }
}
```

## MCP Tool Implementations

### 1. Balance Query with SecretJS

```typescript
async function executeSecretQueryBalanceJS(arguments: any) {
    const { address, denom = 'uscrt' } = arguments;
    
    try {
        // Use SecretJS query method
        const balanceResponse = await this.queryClient.query.bank.balance({
            address: address,
            denom: denom
        });
        
        const balance = balanceResponse.balance;
        
        if (!balance || balance.amount === '0') {
            return {
                content: [{
                    type: 'text',
                    text: `No ${denom} balance found for ${address}`
                }],
                isError: false
            };
        }
        
        // Format response based on denomination
        let displayText: string;
        if (denom === 'uscrt') {
            const scrtAmount = Number(balance.amount) / 1_000_000;
            displayText = `Balance: ${scrtAmount.toFixed(6)} SCRT (${balance.amount} uscrt)`;
        } else {
            displayText = `Balance: ${balance.amount} ${balance.denom}`;
        }
        
        return {
            content: [{
                type: 'text',
                text: `${address}\n${displayText}`
            }],
            isError: false
        };
        
    } catch (error) {
        return {
            content: [{
                type: 'text',
                text: `Error querying balance: ${error instanceof Error ? error.message : String(error)}`
            }],
            isError: true
        };
    }
}
```

### 2. All Balances Query

```typescript
async function executeSecretQueryAllBalancesJS(arguments: any) {
    const { address } = arguments;
    
    try {
        // Query all balances using SecretJS
        const response = await this.queryClient.query.bank.allBalances({
            address: address
        });
        
        const balances = response.balances;
        
        if (!balances || balances.length === 0) {
            return {
                content: [{
                    type: 'text',
                    text: `No balances found for ${address}`
                }],
                isError: false
            };
        }
        
        // Format balance display
        const balanceLines = [`Balances for ${address}:`];
        
        for (const balance of balances) {
            if (balance.denom === 'uscrt') {
                const scrtAmount = Number(balance.amount) / 1_000_000;
                balanceLines.push(`  ${scrtAmount.toFixed(6)} SCRT`);
            } else {
                balanceLines.push(`  ${balance.amount} ${balance.denom}`);
            }
        }
        
        return {
            content: [{
                type: 'text',
                text: balanceLines.join('\n')
            }],
            isError: false
        };
        
    } catch (error) {
        return {
            content: [{
                type: 'text',
                text: `Error querying balances: ${error instanceof Error ? error.message : String(error)}`
            }],
            isError: true
        };
    }
}
```

### 3. Block Height and Network Info

```typescript
async function executeSecretQueryNetworkInfoJS(arguments: any) {
    try {
        // Get latest block using SecretJS
        const latestBlock = await this.queryClient.query.tendermint.getLatestBlock();
        
        // Get node info
        const nodeInfo = await this.queryClient.query.tendermint.getNodeInfo();
        
        const blockHeight = latestBlock.block?.header?.height || 'Unknown';
        const blockTime = latestBlock.block?.header?.time || 'Unknown';
        const chainId = nodeInfo.nodeInfo?.network || 'Unknown';
        
        const infoText = `Secret Network Status:
Chain ID: ${chainId}
Current Block Height: ${blockHeight}
Latest Block Time: ${blockTime}
Node Version: ${nodeInfo.nodeInfo?.version || 'Unknown'}`;
        
        return {
            content: [{
                type: 'text',
                text: infoText
            }],
            isError: false
        };
        
    } catch (error) {
        return {
            content: [{
                type: 'text',
                text: `Error querying network info: ${error instanceof Error ? error.message : String(error)}`
            }],
            isError: true
        };
    }
}
```

### 4. Transaction Query

```typescript
async function executeSecretQueryTransactionJS(arguments: any) {
    const { tx_hash } = arguments;
    
    try {
        // Query transaction using SecretJS
        const txResponse = await this.queryClient.query.getTx(tx_hash);
        
        if (!txResponse) {
            return {
                content: [{
                    type: 'text',
                    text: `Transaction not found: ${tx_hash}`
                }],
                isError: true
            };
        }
        
        // Extract transaction info
        const tx = txResponse;
        const code = tx.code || 0;
        const status = code === 0 ? 'Success' : 'Failed';
        
        // Format gas info
        const gasWanted = tx.gasWanted || 'Unknown';
        const gasUsed = tx.gasUsed || 'Unknown';
        
        // Format transaction details
        const txText = `Transaction ${tx_hash}:
Status: ${status}
Block Height: ${tx.height}
Gas Wanted: ${gasWanted}
Gas Used: ${gasUsed}
Fee: ${tx.fee ? JSON.stringify(tx.fee) : 'None'}
Memo: ${tx.memo || 'None'}`;
        
        return {
            content: [{
                type: 'text',
                text: txText
            }],
            isError: false
        };
        
    } catch (error) {
        return {
            content: [{
                type: 'text',
                text: `Error querying transaction: ${error instanceof Error ? error.message : String(error)}`
            }],
            isError: true
        };
    }
}
```

## Advanced SecretJS Features

### 1. Contract Query Preparation (Phase 2)

```typescript
// Example for future Secret smart contract queries
async function executeSecretQueryContractJS(arguments: any) {
    const { contractAddress, codeHash, query } = arguments;
    
    try {
        const response = await this.queryClient.query.compute.queryContract({
            contract_address: contractAddress,
            code_hash: codeHash, // Optional but much faster
            query: query
        });
        
        return {
            content: [{
                type: 'text',
                text: `Contract Query Result:\n${JSON.stringify(response, null, 2)}`
            }],
            isError: false
        };
        
    } catch (error) {
        return {
            content: [{
                type: 'text',
                text: `Error querying contract: ${error instanceof Error ? error.message : String(error)}`
            }],
            isError: true
        };
    }
}
```

### 2. Validator and Staking Queries

```typescript
async function executeSecretQueryValidatorsJS(arguments: any) {
    try {
        const validators = await this.queryClient.query.staking.validators({
            status: 'BOND_STATUS_BONDED' // Active validators only
        });
        
        const validatorList = validators.validators
            .slice(0, 10) // Top 10 validators
            .map((v, index) => {
                const moniker = v.description?.moniker || 'Unknown';
                const commission = v.commission?.commissionRates?.rate || 'Unknown';
                return `${index + 1}. ${moniker} (Commission: ${commission})`;
            })
            .join('\n');
        
        return {
            content: [{
                type: 'text',
                text: `Top 10 Secret Network Validators:\n${validatorList}`
            }],
            isError: false
        };
        
    } catch (error) {
        return {
            content: [{
                type: 'text',
                text: `Error querying validators: ${error instanceof Error ? error.message : String(error)}`
            }],
            isError: true
        };
    }
}
```

## Error Handling and Retry Logic

### Connection Retry Pattern

```typescript
class RobustSecretJSClient {
    private clients: SecretNetworkClient[] = [];
    private currentClientIndex = 0;
    
    constructor(endpoints: string[], chainId: string) {
        this.clients = endpoints.map(url => 
            new SecretNetworkClient({ url, chainId })
        );
    }
    
    async queryWithRetry<T>(
        queryFn: (client: SecretNetworkClient) => Promise<T>,
        maxRetries = 3
    ): Promise<T> {
        let lastError: Error;
        
        for (let attempt = 0; attempt < maxRetries; attempt++) {
            for (let clientIndex = 0; clientIndex < this.clients.length; clientIndex++) {
                try {
                    const client = this.clients[this.currentClientIndex];
                    const result = await queryFn(client);
                    return result;
                    
                } catch (error) {
                    lastError = error instanceof Error ? error : new Error(String(error));
                    
                    // Try next client
                    this.currentClientIndex = (this.currentClientIndex + 1) % this.clients.length;
                    
                    // Log retry attempt
                    console.warn(`Query attempt ${attempt + 1} failed, trying next endpoint:`, error);
                }
            }
            
            // Wait before retrying all endpoints
            if (attempt < maxRetries - 1) {
                await new Promise(resolve => setTimeout(resolve, 1000 * (attempt + 1)));
            }
        }
        
        throw lastError!;
    }
}
```

### Usage in MCP Tools

```typescript
class SecretJSMCPService {
    private robustClient: RobustSecretJSClient;
    
    constructor(network: 'mainnet' | 'testnet') {
        const config = this.getNetworkConfig(network);
        this.robustClient = new RobustSecretJSClient(config.endpoints, config.chainId);
    }
    
    async executeBalanceQuery(arguments: any) {
        return await this.robustClient.queryWithRetry(async (client) => {
            return await client.query.bank.balance({
                address: arguments.address,
                denom: arguments.denom || 'uscrt'
            });
        });
    }
}
```

## Integration with Hub Router

### TypeScript Support in secretGPT

```typescript
// Type definitions for MCP tool responses
interface MCPToolResponse {
    content: Array<{
        type: 'text' | 'image';
        text?: string;
        data?: string;
        mimeType?: string;
    }>;
    isError: boolean;
}

// SecretJS MCP tool provider
class SecretJSToolProvider {
    private secretClient: SecretJSMCPService;
    
    constructor(network: 'mainnet' | 'testnet' = 'mainnet') {
        this.secretClient = new SecretJSMCPService(network);
    }
    
    async getTools(): Promise<Array<any>> {
        return [
            {
                name: 'secret_query_balance_js',
                description: 'Query SCRT balance using SecretJS library',
                inputSchema: {
                    type: 'object',
                    properties: {
                        address: { type: 'string', pattern: '^secret1[a-z0-9]{38}$' },
                        denom: { type: 'string', default: 'uscrt' }
                    },
                    required: ['address']
                }
            }
            // ... other tools
        ];
    }
    
    async executeTool(toolName: string, arguments: any): Promise<MCPToolResponse> {
        switch (toolName) {
            case 'secret_query_balance_js':
                return await this.secretClient.executeBalanceQuery(arguments);
            // ... other cases
            default:
                throw new Error(`Unknown tool: ${toolName}`);
        }
    }
}
```

## Performance Optimization

### 1. Connection Pooling

```typescript
class OptimizedSecretJSClient {
    private connectionPool: Map<string, SecretNetworkClient> = new Map();
    
    getClient(endpoint: string, chainId: string): SecretNetworkClient {
        const key = `${endpoint}:${chainId}`;
        
        if (!this.connectionPool.has(key)) {
            this.connectionPool.set(key, new SecretNetworkClient({
                url: endpoint,
                chainId: chainId
            }));
        }
        
        return this.connectionPool.get(key)!;
    }
}
```

### 2. Response Caching

```typescript
class CachedSecretJSClient {
    private cache = new Map<string, { data: any; timestamp: number }>();
    private cacheTTL = 30000; // 30 seconds
    
    async cachedQuery<T>(
        cacheKey: string, 
        queryFn: () => Promise<T>
    ): Promise<T> {
        const cached = this.cache.get(cacheKey);
        const now = Date.now();
        
        if (cached && (now - cached.timestamp) < this.cacheTTL) {
            return cached.data;
        }
        
        const result = await queryFn();
        this.cache.set(cacheKey, { data: result, timestamp: now });
        
        return result;
    }
}
```

## Future Keplr Integration (Phase 2)

### Signing Client Setup

```typescript
async function setupKeplrSigningClient(): Promise<SecretNetworkClient> {
    // Enable Keplr for Secret Network
    await window.keplr.enable('secret-4');
    
    // Get offline signer
    const offlineSigner = window.getOfflineSignerOnlyAmino('secret-4');
    const accounts = await offlineSigner.getAccounts();
    
    // Create signing client
    const signingClient = new SecretNetworkClient({
        url: 'https://lcd.mainnet.secretsaturn.net',
        chainId: 'secret-4',
        wallet: offlineSigner,
        walletAddress: accounts[0].address,
        encryptionUtils: window.getEnigmaUtils('secret-4')
    });
    
    return signingClient;
}
```

---

**Next Steps:**
1. **Implement basic SecretJS integration** for query tools
2. **Test with multiple endpoints** for reliability  
3. **Add caching layer** for performance
4. **Prepare Keplr integration** for Phase 2 transactions
