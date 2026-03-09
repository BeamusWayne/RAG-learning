import { Agent } from '@anthropic-ai/claude-agent-sdk';
import { OpenAI } from 'openai';
import * as fs from 'fs';
import * as readline from 'readline';

interface AgentInput {
  prompt: string;
  sessionId?: string;
  groupFolder: string;
  chatJid: string;
  isMain: boolean;
  assistantName: string;
}

interface AgentOutput {
  result?: string | null;
  status: 'success' | 'error';
  error?: string;
  newSessionId?: string;
}

async function readInput(): Promise<AgentInput> {
  return new Promise((resolve, reject) => {
    let data = '';
    process.stdin.setEncoding('utf-8');
    process.stdin.on('data', (chunk) => {
      data += chunk;
    });
    process.stdin.on('end', () => {
      try {
        resolve(JSON.parse(data));
      } catch (err) {
        reject(new Error(`Failed to parse input JSON: ${err}`));
      }
    });
    process.stdin.on('error', reject);
  });
}

function writeOutput(output: AgentOutput): void {
  process.stdout.write(JSON.stringify(output) + '\n');
}

async function runQwenAgent(input: AgentInput): Promise<AgentOutput> {
  const apiKey = process.env.DASHSCOPE_API_KEY;
  const baseURL = process.env.DASHSCOPE_BASE_URL || 'https://dashscope.aliyuncs.com/compatible-mode/v1';

  if (!apiKey) {
    return {
      status: 'error',
      error: 'DASHSCOPE_API_KEY not set',
    };
  }

  const client = new OpenAI({
    apiKey,
    baseURL,
  });

  try {
    const systemPrompt = `You are ${input.assistantName}, a helpful AI assistant.
You are running in an isolated container environment with access to:
- File system operations (read, write, edit files)
- Web search and fetch capabilities
- Browser automation
- Scheduled task management

Always be concise and helpful. Format your responses clearly.`;

    const messages: any[] = [
      { role: 'system', content: systemPrompt },
      { role: 'user', content: input.prompt },
    ];

    const response = await client.chat.completions.create({
      model: 'qwen-plus',
      messages,
      stream: false,
      temperature: 0.7,
      max_tokens: 4096,
    });

    const result = response.choices[0]?.message?.content || '';

    return {
      result,
      status: 'success',
      newSessionId: input.sessionId || `session_${Date.now()}`,
    };
  } catch (err) {
    return {
      status: 'error',
      error: err instanceof Error ? err.message : 'Unknown error',
    };
  }
}

async function main(): Promise<void> {
  try {
    const input = await readInput();
    const output = await runQwenAgent(input);
    writeOutput(output);
    process.exit(0);
  } catch (err) {
    writeOutput({
      status: 'error',
      error: err instanceof Error ? err.message : 'Unknown error',
    });
    process.exit(1);
  }
}

main();
