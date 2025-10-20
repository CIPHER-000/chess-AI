import OpenAI from "openai";
import { GPT5Request, CodeAnalysisRequest } from "./types";

export class GPT5Client {
  private client: OpenAI;

  constructor() {
    this.client = new OpenAI({
      apiKey: process.env.OPENAI_API_KEY,
    });
  }

  async askGPT5(request: GPT5Request): Promise<string> {
    try {
      const response = await this.client.responses.create({
        model: "gpt-5",
        input: request.prompt,
        temperature: request.temperature || 0.7,
        max_output_tokens: request.maxTokens || 1000,
      });

      return response.output_text;
    } catch (error) {
      console.error("Error calling GPT-5:", error);
      throw new Error(`Failed to call GPT-5: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  async analyzeCode(request: CodeAnalysisRequest): Promise<string> {
    const systemPrompt = `You are an expert React and TypeScript developer. Analyze the provided code and answer the user's question.
Focus on React hooks, state management, and best practices. Provide specific, actionable advice.`;

    const userPrompt = `Please analyze this React/TypeScript code:

${request.code}

Context: ${request.context || 'React component with hooks'}

Question: ${request.question || 'Please analyze this code for potential issues and improvements.'}

Provide a detailed analysis including:
1. Any issues or potential problems
2. Suggestions for improvement
3. Best practices recommendations`;

    try {
      const response = await this.client.responses.create({
        model: "gpt-5",
        input: userPrompt,
        temperature: 0.3,
        max_output_tokens: 2000,
      });

      return response.output_text;
    } catch (error) {
      console.error("Error analyzing code with GPT-5:", error);
      throw new Error(`Failed to analyze code: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  async collaborateOnProblem(problem: string, context?: string): Promise<string> {
    const systemPrompt = `You are an expert AI collaborator working with another AI assistant to solve complex programming problems.
Provide detailed, well-reasoned analysis and solutions. Think step by step and explain your reasoning.`;

    const userPrompt = `I need your expertise to solve this programming problem:

Problem: ${problem}

Context: ${context || 'Working on a React application with hooks and state management issues'}

Please help me:
1. Analyze the problem thoroughly
2. Identify potential root causes
3. Propose multiple solution approaches
4. Recommend the best approach with detailed reasoning
5. Provide implementation guidance

Collaborate with me to find the best solution.`;

    try {
      const response = await this.client.responses.create({
        model: "gpt-5",
        input: userPrompt,
        temperature: 0.5,
        max_output_tokens: 3000,
      });

      return response.output_text;
    } catch (error) {
      console.error("Error collaborating with GPT-5:", error);
      throw new Error(`Failed to collaborate: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }
}