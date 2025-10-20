import express, { Request, Response } from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import { GPT5Client } from './openai';
import { MCPRequest, MCPResponse, MCPTool } from './types';

dotenv.config();

const app = express();
const port = process.env.PORT || 3001;

// Initialize GPT-5 client
const gpt5Client = new GPT5Client();

// Middleware
app.use(cors());
app.use(express.json());

// MCP Tools definition
const tools: MCPTool[] = [
  {
    name: "ask_gpt5",
    description: "Ask GPT-5 a question or get assistance with any topic",
    inputSchema: {
      type: "object",
      properties: {
        prompt: {
          type: "string",
          description: "The question or prompt to send to GPT-5"
        },
        system: {
          type: "string",
          description: "Optional system message to guide GPT-5's response"
        },
        temperature: {
          type: "number",
          description: "Optional temperature (0.0-1.0) for response randomness",
          minimum: 0,
          maximum: 1
        },
        maxTokens: {
          type: "integer",
          description: "Optional maximum tokens for the response",
          minimum: 1,
          maximum: 4000
        }
      },
      required: ["prompt"]
    }
  },
  {
    name: "analyze_code_with_gpt5",
    description: "Analyze code with GPT-5 to identify issues and get suggestions",
    inputSchema: {
      type: "object",
      properties: {
        code: {
          type: "string",
          description: "The code to analyze"
        },
        context: {
          type: "string",
          description: "Optional context about the code (e.g., 'React component', 'utility function')"
        },
        question: {
          type: "string",
          description: "Optional specific question about the code"
        }
      },
      required: ["code"]
    }
  },
  {
    name: "collaborate_with_gpt5",
    description: "Collaborate with GPT-5 to solve complex programming problems",
    inputSchema: {
      type: "object",
      properties: {
        problem: {
          type: "string",
          description: "The programming problem to solve"
        },
        context: {
          type: "string",
          description: "Optional context about the problem or project"
        }
      },
      required: ["problem"]
    }
  }
];

// MCP Protocol endpoints
app.post('/mcp', async (req: Request, res: Response) => {
  try {
    const mcpRequest: MCPRequest = req.body;

    if (!mcpRequest.method) {
      return res.status(400).json({
        jsonrpc: "2.0",
        id: mcpRequest.id || 0,
        error: {
          code: -32600,
          message: "Invalid Request: missing method"
        }
      });
    }

    const response: MCPResponse = {
      jsonrpc: "2.0",
      id: mcpRequest.id || 0
    };

    // Handle different MCP methods
    switch (mcpRequest.method) {
      case "initialize":
        response.result = {
          protocolVersion: "2024-11-05",
          capabilities: {
            tools: {}
          },
          serverInfo: {
            name: "mcp-gpt5-server",
            version: "1.0.0"
          }
        };
        break;

      case "tools/list":
        response.result = { tools };
        break;

      case "tools/call":
        const { name, arguments: args } = mcpRequest.params;

        if (!name || !args) {
          response.error = {
            code: -32602,
            message: "Invalid params: missing name or arguments"
          };
          break;
        }

        try {
          switch (name) {
            case "ask_gpt5":
              response.result = {
                content: [
                  {
                    type: "text",
                    text: await gpt5Client.askGPT5({
                      prompt: args.prompt,
                      system: args.system,
                      temperature: args.temperature,
                      maxTokens: args.maxTokens
                    })
                  }
                ]
              };
              break;

            case "analyze_code_with_gpt5":
              response.result = {
                content: [
                  {
                    type: "text",
                    text: await gpt5Client.analyzeCode({
                      code: args.code,
                      context: args.context,
                      question: args.question
                    })
                  }
                ]
              };
              break;

            case "collaborate_with_gpt5":
              response.result = {
                content: [
                  {
                    type: "text",
                    text: await gpt5Client.collaborateOnProblem(
                      args.problem,
                      args.context
                    )
                  }
                ]
              };
              break;

            default:
              response.error = {
                code: -32601,
                message: `Unknown tool: ${name}`
              };
          }
        } catch (error) {
          response.error = {
            code: -32603,
            message: `Internal error: ${error instanceof Error ? error.message : 'Unknown error'}`
          };
        }
        break;

      default:
        response.error = {
          code: -32601,
          message: `Method not found: ${mcpRequest.method}`
        };
    }

    res.json(response);
  } catch (error) {
    console.error('MCP Server Error:', error);
    res.status(500).json({
      jsonrpc: "2.0",
      id: 0,
      error: {
        code: -32603,
        message: "Internal server error"
      }
    });
  }
});

// Health check endpoint
app.get('/health', (req: Request, res: Response) => {
  res.json({ status: 'ok', server: 'mcp-gpt5-server' });
});

// Start server
app.listen(port, () => {
  console.log(`🚀 MCP GPT-5 Server running on port ${port}`);
  console.log(`📋 Available tools: ${tools.map(t => t.name).join(', ')}`);
  console.log(`🔗 MCP endpoint: http://localhost:${port}/mcp`);
});

export default app;