# Secret Network MCP Tools

**Purpose**: Read-only blockchain query tools for Secret Network integration  
**Phase**: Initial implementation - queries only, transactions later with Keplr wallet integration  
**Reference**: Cosmos SDK Bank module, Secret Network LCD/RPC APIs

## Overview

This document defines MCP tools for querying Secret Network blockchain data. These tools provide read-only access to blockchain information such as account balances, block data, and transaction details through secretGPT's MCP integration.

**Current Scope**: Read-only queries (balances, block height, transaction lookup)  
**Future Scope**: Transaction submission via Keplr wallet integration in web UI

## Tool Categories

### Account Query Tools

#### 1. Query Account Balance

**Tool Definition:**
```json
{
  "name": "secret_query_balance",
  "description": "Query SCRT balance for a Secret Network address",
  "inputSchema": {
    "type": "object",
    "properties": {
      "address": {
        "type": "string",
        "description": "Secret Network address (secret1...)",
        "pattern": "^secret1[a-z0-9]{38}$"
      },
      "denom": {
        "type": "string", 
        "description": "Token denomination (default: uscrt)",
        "default": "uscrt"
      }
    },
    "required": ["address"]
  },
  "annotations": {
    "title": "Secret Network Balance Query",
    "readOnlyHint": true,
    "destructiveHint": false,
    "openWorldHint": true
  }
}
```

**API Implementation:**
```python
async def execute_secret_query_balance(self, arguments):
    """Query account balance using Secret Network LCD API"""
    
    address = arguments["address"]
    denom = arguments.get("denom", "uscrt")
    
    # Use Cosmos SDK bank module REST endpoint
    # Pattern: /cosmos/bank/v1beta1/balances/{address}/by_denom?denom={denom}
    url = f"{self.lcd_endpoint}/cosmos/bank/v1beta1/balances/{address}/by_denom"
    params = {"denom": denom}
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            
        data = response.json()
        balance = data.get("balance", {})
        
        # Convert from micro-units to SCRT for display
        amount_uscrt = int(balance.get("amount", "0"))
        amount_scrt = amount_uscrt / 1_000_000
        
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Balance for {address}:\n{amount_scrt:.6f} SCRT ({amount_uscrt} uscrt)"
                }
            ],
            "isError": False
        }
        
    except Exception as e:
        return {
            "content": [
                {
                    "type": "text", 
                    "text": f"Error querying balance: {str(e)}"
                }
            ],
            "isError": True
        }
```

#### 2. Query All Account Balances

**Tool Definition:**
```json
{
  "name": "secret_query_all_balances",
  "description": "Query all token balances for a Secret Network address",
  "inputSchema": {
    "type": "object",
    "properties": {
      "address": {
        "type": "string",
        "description": "Secret Network address (secret1...)",
        "pattern": "^secret1[a-z0-9]{38}$"
      }
    },
    "required": ["address"]
  }
}
```

**API Implementation:**
```python
async def execute_secret_query_all_balances(self, arguments):
    """Query all balances using Secret Network LCD API"""
    
    address = arguments["address"]
    
    # Use Cosmos SDK bank module REST endpoint
    # Pattern: /cosmos/bank/v1beta1/balances/{address}
    url = f"{self.lcd_endpoint}/cosmos/bank/v1beta1/balances/{address}"
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            
        data = response.json()
        balances = data.get("balances", [])
        
        if not balances:
            balance_text = f"No balances found for {address}"
        else:
            balance_lines = [f"Balances for {address}:"]
            for balance in balances:
                denom = balance["denom"]
                amount = int(balance["amount"])
                
                # Format SCRT specially
                if denom == "uscrt":
                    scrt_amount = amount / 1_000_000
                    balance_lines.append(f"  {scrt_amount:.6f} SCRT")
                else:
                    balance_lines.append(f"  {amount} {denom}")
            
            balance_text = "\n".join(balance_lines)
        
        return {
            "content": [
                {
                    "type": "text",
                    "text": balance_text
                }
            ],
            "isError": False
        }
        
    except Exception as e:
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Error querying balances: {str(e)}"
                }
            ],
            "isError": True
        }
```

### Blockchain Query Tools

#### 3. Query Current Block Height

**Tool Definition:**
```json
{
  "name": "secret_query_block_height",
  "description": "Get the current block height of Secret Network",
  "inputSchema": {
    "type": "object",
    "properties": {},
    "additionalProperties": false
  }
}
```

**API Implementation:**
```python
async def execute_secret_query_block_height(self, arguments):
    """Query current block height using Tendermint RPC"""
    
    # Use Tendermint RPC status endpoint
    url = f"{self.rpc_endpoint}/status"
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            
        data = response.json()
        latest_block_height = data["result"]["sync_info"]["latest_block_height"]
        latest_block_time = data["result"]["sync_info"]["latest_block_time"]
        
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Secret Network Status:\nCurrent Block Height: {latest_block_height}\nLatest Block Time: {latest_block_time}"
                }
            ],
            "isError": False
        }
        
    except Exception as e:
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Error querying block height: {str(e)}"
                }
            ],
            "isError": True
        }
```

#### 4. Query Block by Height

**Tool Definition:**
```json
{
  "name": "secret_query_block",
  "description": "Get block information by height",
  "inputSchema": {
    "type": "object",
    "properties": {
      "height": {
        "type": "integer",
        "description": "Block height to query",
        "minimum": 1
      }
    },
    "required": ["height"]
  }
}
```

**API Implementation:**
```python
async def execute_secret_query_block(self, arguments):
    """Query block by height using Tendermint RPC"""
    
    height = arguments["height"]
    
    # Use Tendermint RPC block endpoint  
    url = f"{self.rpc_endpoint}/block"
    params = {"height": str(height)}
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            
        data = response.json()
        block = data["result"]["block"]
        header = block["header"]
        
        block_info = {
            "height": header["height"],
            "time": header["time"],
            "proposer": header["proposer_address"],
            "num_txs": len(block["data"]["txs"]),
            "hash": data["result"]["block_id"]["hash"]
        }
        
        info_text = f"""Block {height} Information:
Height: {block_info['height']}
Time: {block_info['time']}
Hash: {block_info['hash']}
Number of Transactions: {block_info['num_txs']}
Proposer: {block_info['proposer']}"""
        
        return {
            "content": [
                {
                    "type": "text",
                    "text": info_text
                }
            ],
            "isError": False
        }
        
    except Exception as e:
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Error querying block {height}: {str(e)}"
                }
            ],
            "isError": True
        }
```

### Transaction Query Tools

#### 5. Query Transaction by Hash

**Tool Definition:**
```json
{
  "name": "secret_query_transaction",
  "description": "Get transaction details by transaction hash",
  "inputSchema": {
    "type": "object",
    "properties": {
      "tx_hash": {
        "type": "string",
        "description": "Transaction hash (64 character hex string)",
        "pattern": "^[A-Fa-f0-9]{64}$"
      }
    },
    "required": ["tx_hash"]
  }
}
```

**API Implementation:**
```python
async def execute_secret_query_transaction(self, arguments):
    """Query transaction by hash using Tendermint RPC"""
    
    tx_hash = arguments["tx_hash"].upper()
    
    # Use Tendermint RPC tx endpoint
    url = f"{self.rpc_endpoint}/tx"
    params = {"hash": f"0x{tx_hash}"}
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            
        data = response.json()
        
        if "error" in data:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Transaction not found: {tx_hash}"
                    }
                ],
                "isError": True
            }
        
        tx_result = data["result"]
        tx_info = {
            "hash": tx_result["hash"],
            "height": tx_result["height"],
            "code": tx_result["tx_result"]["code"],
            "gas_wanted": tx_result["tx_result"]["gas_wanted"],
            "gas_used": tx_result["tx_result"]["gas_used"],
            "log": tx_result["tx_result"]["log"]
        }
        
        # Determine status
        status = "Success" if tx_info["code"] == 0 else "Failed"
        
        tx_text = f"""Transaction {tx_hash}:
Status: {status}
Block Height: {tx_info['height']}
Gas Wanted: {tx_info['gas_wanted']}
Gas Used: {tx_info['gas_used']}
Log: {tx_info['log'][:200]}{'...' if len(tx_info['log']) > 200 else ''}"""
        
        return {
            "content": [
                {
                    "type": "text",
                    "text": tx_text
                }
            ],
            "isError": False
        }
        
    except Exception as e:
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Error querying transaction {tx_hash}: {str(e)}"
                }
            ],
            "isError": True
        }
```

## MCP Server Configuration

### Server Setup

```python
class SecretNetworkMCPServer:
    """MCP Server for Secret Network blockchain queries"""
    
    def __init__(self, network="mainnet"):
        self.network = network
        
        # API endpoints based on network
        if network == "mainnet":
            self.lcd_endpoint = "https://lcd.mainnet.secretsaturn.net"
            self.rpc_endpoint = "https://rpc.mainnet.secretsaturn.net"
        elif network == "testnet":
            self.lcd_endpoint = "https://lcd.testnet.secretsaturn.net" 
            self.rpc_endpoint = "https://rpc.testnet.secretsaturn.net"
        else:
            raise ValueError(f"Unsupported network: {network}")
        
        # Tool registry
        self.tools = {
            "secret_query_balance": self.execute_secret_query_balance,
            "secret_query_all_balances": self.execute_secret_query_all_balances,
            "secret_query_block_height": self.execute_secret_query_block_height,
            "secret_query_block": self.execute_secret_query_block,
            "secret_query_transaction": self.execute_secret_query_transaction,
        }
    
    async def list_tools(self):
        """Return list of available tools"""
        return [
            # Tool definitions from above...
        ]
    
    async def call_tool(self, name, arguments):
        """Execute tool by name"""
        if name not in self.tools:
            raise ValueError(f"Unknown tool: {name}")
        
        return await self.tools[name](arguments)
```

### Hub Integration

```python
# In secretGPT hub router integration
class SecretNetworkToolProvider:
    """Provides Secret Network tools to MCP service"""
    
    def __init__(self, network="mainnet"):
        self.server = SecretNetworkMCPServer(network)
    
    async def get_tools(self):
        """Get tools for MCP service registration"""
        return await self.server.list_tools()
    
    async def execute_tool(self, tool_name, arguments):
        """Execute Secret Network tool"""
        return await self.server.call_tool(tool_name, arguments)

# Register with MCP service
mcp_service.register_tool_provider("secret_network", SecretNetworkToolProvider())
```

## Network Configuration

### API Endpoints

**Mainnet (secret-4):**
- **LCD**: https://lcd.mainnet.secretsaturn.net
- **RPC**: https://rpc.mainnet.secretsaturn.net
- **Alternative LCD**: https://secretnetwork-api.lavenderfive.com:443

**Testnet (pulsar-3):**
- **LCD**: https://lcd.testnet.secretsaturn.net
- **RPC**: https://rpc.testnet.secretsaturn.net

### Alternative Endpoints

For production use, consider multiple endpoints with failover:

```python
MAINNET_ENDPOINTS = {
    "lcd": [
        "https://lcd.mainnet.secretsaturn.net",
        "https://secretnetwork-api.lavenderfive.com:443",
        "https://rest-secret.01node.com"
    ],
    "rpc": [
        "https://rpc.mainnet.secretsaturn.net", 
        "https://secretnetwork-rpc.lavenderfive.com:443",
        "https://rpc-secret.01node.com"
    ]
}
```

## Error Handling

### Common Error Scenarios

1. **Invalid Address Format**
   - Validate secret1... format with regex
   - Return user-friendly error message

2. **Network Connectivity Issues**
   - Implement retry logic with exponential backoff
   - Try alternative endpoints on failure

3. **API Rate Limiting**
   - Implement request throttling
   - Cache responses for repeated queries

4. **Invalid Block Height/Transaction Hash**
   - Validate input formats
   - Return specific error messages

### Error Response Format

```python
def format_error_response(error_message, error_type="query_error"):
    """Format consistent error responses"""
    return {
        "content": [
            {
                "type": "text",
                "text": f"Secret Network Query Error: {error_message}"
            }
        ],
        "isError": True,
        "error_type": error_type
    }
```

## Future Enhancements

### Phase 2: Transaction Tools (with Keplr Integration)

**Planned Tools:**
- `secret_send_tokens` - Send SCRT tokens to another address
- `secret_delegate_tokens` - Delegate SCRT to validators  
- `secret_vote_proposal` - Vote on governance proposals
- `secret_execute_contract` - Execute Secret smart contracts

**Keplr Integration Requirements:**
- Web UI wallet connection
- Transaction signing in browser
- Gas estimation and fee calculation
- Transaction broadcasting

### Phase 3: Advanced Query Tools

**Smart Contract Tools:**
- `secret_query_contract` - Query Secret smart contract state
- `secret_list_contracts` - List deployed contracts
- `secret_contract_history` - Contract interaction history

**Governance Tools:**  
- `secret_list_proposals` - List governance proposals
- `secret_query_proposal` - Get proposal details
- `secret_query_vote` - Check vote status

### Phase 4: Analytics Tools

**Network Analytics:**
- `secret_validator_info` - Validator performance data
- `secret_network_stats` - Network statistics and metrics
- `secret_supply_info` - Token supply and distribution

## Security Considerations

### Input Validation
- Address format validation (secret1... pattern)
- Transaction hash format validation (64-char hex)
- Block height range validation
- Parameter sanitization

### Rate Limiting
- Implement client-side rate limiting
- Use multiple API endpoints for load distribution
- Cache frequently requested data

### Data Privacy
- No sensitive data logging
- Secure endpoint configuration
- HTTPS-only connections

---

**Implementation Priority:**
1. Start with balance and block height queries
2. Add transaction lookup capability  
3. Test integration with AttestAI web UI
4. Plan Keplr wallet integration for Phase 2
