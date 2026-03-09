import fs from 'fs';
import path from 'path';

const ENV_PATH = path.join(process.cwd(), '.env');

export function readEnvFile(keys?: string[]): Record<string, string> {
  const result: Record<string, string> = {};

  if (!fs.existsSync(ENV_PATH)) {
    return result;
  }

  const content = fs.readFileSync(ENV_PATH, 'utf-8');
  const lines = content.split('\n');

  for (const line of lines) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith('#')) {
      continue;
    }

    const match = trimmed.match(/^([^=]+)=(.*)$/);
    if (!match) {
      continue;
    }

    const key = match[1].trim();
    const value = match[2].trim();

    if (!keys || keys.includes(key)) {
      result[key] = value;
    }
  }

  return result;
}
