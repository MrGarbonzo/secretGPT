#!/usr/bin/env node

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  ListToolsRequestSchema,
  CallToolRequestSchema,
  ErrorCode,
  McpError,
} from '@modelcontextprotocol/sdk/types.js';
import { z } from 'zod';
import { SecretNetworkClient } from 'secretjs';

// Server configuration
const server = new Server(
  {
    name: 'secret-network-mcp-server',
    version: '1.0.0',
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// Secret Network client instance
let secretClient: SecretNetworkClient | null = null;

// Initialize Secret Network client
async function initializeSecretClient(): Promise<void> {
  try {
    const nodeUrl = process.env.SECRET_NODE_URL || 'https://rpc.ankr.com/http/scrt_cosmos';
    const chainId = process.env.SECRET_CHAIN_ID || 'secret-4';
    
    secretClient = new SecretNetworkClient({
      url: nodeUrl,
      chainId: chainId,
    });
    
    console.error('Secret Network client initialized successfully');
    console.error(`Connected to: ${nodeUrl}`);
    console.error(`Chain ID: ${chainId}`);
  } catch (error) {
    console.error('Failed to initialize Secret Network client:', error);
    throw error;
  }
}

// Validation schemas for tool arguments
const BalanceQuerySchema = z.object({
  address: z.string().regex(/^secret1[a-z0-9]+$/, 'Invalid Secret Network address'),
});

const BlockQuerySchema = z.object({
  height: z.number().int().positive().optional(),
});

const AccountQuerySchema = z.object({
  address: z.string().regex(/^secret1[a-z0-9]+$/, 'Invalid Secret Network address'),
});

const TransactionQuerySchema = z.object({
  txHash: z.string().length(64, 'Transaction hash must be 64 characters'),
});

const ContractQuerySchema = z.object({
  contractAddress: z.string().regex(/^secret1[a-z0-9]+$/, 'Invalid Secret Network contract address'),
  query: z.record(z.any()),
});

// List all available tools
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: 'secret_query_balance',
        description: 'Query SCRT balance for a Secret Network address',
        inputSchema: {
          type: 'object',
          properties: {
            address: {
              type: 'string',
              description: 'Secret Network address (secret1...)',
              pattern: '^secret1[a-z0-9]+$',
            },
          },
          required: ['address'],
        },
      },
      {
        name: 'secret_query_block',
        description: 'Query block information from Secret Network',
        inputSchema: {
          type: 'object',
          properties: {
            height: {
              type: 'number',
              description: 'Block height (optional, defaults to latest)',
              minimum: 1,
            },
          },
          required: [],
        },
      },
      {
        name: 'secret_query_account',
        description: 'Query account information for a Secret Network address',
        inputSchema: {
          type: 'object',
          properties: {
            address: {
              type: 'string',
              description: 'Secret Network address (secret1...)',
              pattern: '^secret1[a-z0-9]+$',
            },
          },
          required: ['address'],
        },
      },
      {
        name: 'secret_query_transaction',
        description: 'Query transaction details by hash',
        inputSchema: {
          type: 'object',
          properties: {
            txHash: {
              type: 'string',
              description: 'Transaction hash (64 character hex string)',
              minLength: 64,
              maxLength: 64,
            },
          },
          required: ['txHash'],
        },
      },
      {
        name: 'secret_query_contract',
        description: 'Query a Secret Network smart contract',
        inputSchema: {
          type: 'object',
          properties: {
            contractAddress: {
              type: 'string',
              description: 'Contract address (secret1...)',
              pattern: '^secret1[a-z0-9]+$',
            },
            query: {
              type: 'object',
              description: 'Query object to send to the contract',
            },
          },
          required: ['contractAddress', 'query'],
        },
      },
      {
        name: 'secret_network_status',
        description: 'Get Secret Network node status and chain information',
        inputSchema: {
          type: 'object',
          properties: {},
          required: [],
        },
      },
    ],
  };
});

// Handle tool execution
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  try {
    if (!secretClient) {
      throw new McpError(
        ErrorCode.InternalError,
        'Secret Network client not initialized'
      );
    }

    switch (name) {
      case 'secret_query_balance': {
        const { address } = BalanceQuerySchema.parse(args);
        
        const balance = await secretClient.query.bank.balance({
          address,
          denom: 'uscrt',
        });
        
        const scrtBalance = balance.balance?.amount 
          ? (parseInt(balance.balance.amount) / 1_000_000).toFixed(6)
          : '0.000000';

        return {
          content: [
            {
              type: 'text',
              text: `SCRT Balance for ${address}: ${scrtBalance} SCRT`,
            },
          ],
        };
      }

      case 'secret_query_block': {
        const { height } = BlockQuerySchema.parse(args || {});
        
        const block = height 
          ? await secretClient.query.tendermint.getBlockByHeight({ height: height.toString() })
          : await secretClient.query.tendermint.getLatestBlock({});

        return {
          content: [
            {
              type: 'text',
              text: `Block ${block.block?.header?.height || 'unknown'}\n` +
                   `Time: ${block.block?.header?.time || 'unknown'}\n` +
                   `Hash: ${block.block_id?.hash || 'unknown'}\n` +
                   `Transactions: ${block.block?.data?.txs?.length || 0}`,
            },
          ],
        };
      }

      case 'secret_query_account': {
        const { address } = AccountQuerySchema.parse(args);
        
        const account = await secretClient.query.auth.account({ address });
        
        return {
          content: [
            {
              type: 'text',
              text: `Account: ${address}\n` +
                   `Account Number: ${(account.account as any)?.account_number || 'unknown'}\n` +
                   `Sequence: ${(account.account as any)?.sequence || 'unknown'}\n` +
                   `Type: ${account.account?.['@type'] || 'unknown'}`,
            },
          ],
        };
      }

      case 'secret_query_transaction': {
        const { txHash } = TransactionQuerySchema.parse(args);
        
        const tx = await secretClient.query.getTx(txHash);
        
        if (!tx) {
          return {
            content: [
              {
                type: 'text',
                text: `Transaction ${txHash} not found`,
              },
            ],
            isError: true,
          };
        }

        return {
          content: [
            {
              type: 'text',
              text: `Transaction: ${txHash}\n` +
                   `Block Height: ${tx.height}\n` +
                   `Gas Used: ${tx.gasUsed}/${tx.gasWanted}\n` +
                   `Result: ${tx.code === 0 ? 'Success' : 'Failed'}\n` +
                   `Events: ${tx.events?.length || 0}`,
            },
          ],
        };
      }

      case 'secret_query_contract': {
        const { contractAddress, query } = ContractQuerySchema.parse(args);
        
        try {
          const result = await secretClient.query.compute.queryContract({
            contract_address: contractAddress,
            code_hash: '', // Will be automatically resolved by secretjs
            query,
          });

          return {
            content: [
              {
                type: 'text',
                text: `Contract Query Result:\n${JSON.stringify(result, null, 2)}`,
              },
            ],
          };
        } catch (error) {
          return {
            content: [
              {
                type: 'text',
                text: `Contract query failed: ${error instanceof Error ? error.message : 'Unknown error'}`,
              },
            ],
            isError: true,
          };
        }
      }

      case 'secret_network_status': {
        const status = await secretClient.query.tendermint.getNodeInfo({});
        
        return {
          content: [
            {
              type: 'text',
              text: `Secret Network Status\n` +
                   `Chain ID: ${status.default_node_info?.network || 'unknown'}\n` +
                   `Node Version: ${status.default_node_info?.version || 'unknown'}\n` +
                   `App Version: ${status.application_version?.version || 'unknown'}\n` +
                   `Moniker: ${status.default_node_info?.moniker || 'unknown'}`,
            },
          ],
        };
      }

      default:
        throw new McpError(
          ErrorCode.MethodNotFound,
          `Unknown tool: ${name}`
        );
    }
  } catch (error) {
    if (error instanceof McpError) {
      throw error;
    }

    return {
      content: [
        {
          type: 'text',
          text: `Error executing ${name}: ${error instanceof Error ? error.message : 'Unknown error'}`,
        },
      ],
      isError: true,
    };
  }
});

// Main function to start the server
async function main(): Promise<void> {
  try {
    // Initialize Secret Network client
    await initializeSecretClient();
    
    // Create stdio transport
    const transport = new StdioServerTransport();
    
    // Connect server to transport
    await server.connect(transport);
    
    console.error('Secret Network MCP Server started successfully');
  } catch (error) {
    console.error('Failed to start Secret Network MCP Server:', error);
    process.exit(1);
  }
}

// Start the server
main().catch((error) => {
  console.error('Unhandled error:', error);
  process.exit(1);
});