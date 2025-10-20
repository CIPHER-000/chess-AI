export interface MCPRequest {
  jsonrpc: "2.0";
  id: string | number;
  method: string;
  params?: any;
}

export interface MCPResponse {
  jsonrpc: "2.0";
  id: string | number;
  result?: any;
  error?: {
    code: number;
    message: string;
    data?: any;
  };
}

export interface MCPTool {
  name: string;
  description: string;
  inputSchema: {
    type: "object";
    properties: Record<string, any>;
    required: string[];
  };
}

export interface GPT5Request {
  prompt: string;
  system?: string;
  temperature?: number;
  maxTokens?: number;
}

export interface CodeAnalysisRequest {
  code: string;
  context?: string;
  question?: string;
}