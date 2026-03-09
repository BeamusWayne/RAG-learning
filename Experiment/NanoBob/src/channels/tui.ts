import readline from 'readline';
import { Channel, ChannelOpts, NewMessage } from '../types.js';
import { registerChannel } from './registry.js';
import { logger } from '../logger.js';

export class TUIChannel implements Channel {
  public readonly name = 'tui';
  private connected = false;
  private opts: ChannelOpts;
  private rl?: readline.Interface;
  private messageQueue: string[] = [];
  private isProcessing = false;

  constructor(opts: ChannelOpts) {
    this.opts = opts;
  }

  async connect(): Promise<void> {
    if (this.connected) return;

    this.rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout,
      prompt: '',
    });

    this.printHeader();
    this.connected = true;
    logger.info('TUI channel connected');

    this.startInputLoop();
  }

  private printHeader(): void {
    console.log('\n╔════════════════════════════════════════════╗');
    console.log('║           NanoBob TUI Channel              ║');
    console.log('║           Powered by Qwen                  ║');
    console.log('╠════════════════════════════════════════════╣');
    console.log('║  Type your message and press Enter         ║');
    console.log('║  Type /quit to exit                        ║');
    console.log('║  Type /clear to clear screen               ║');
    console.log('╚════════════════════════════════════════════╝\n');
  }

  private startInputLoop(): void {
    if (!this.rl) return;

    const promptUser = () => {
      if (!this.connected) return;
      
      process.stdout.write('\n\x1b[36mYou:\x1b[0m ');
      this.rl!.question('', (input) => {
        this.handleInput(input);
        promptUser();
      });
    };

    promptUser();
  }

  private handleInput(input: string): void {
    const trimmed = input.trim();
    
    if (!trimmed) return;

    if (trimmed === '/quit') {
      this.disconnect();
      return;
    }

    if (trimmed === '/clear') {
      console.clear();
      this.printHeader();
      return;
    }

    const id = `tui_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    const timestamp = new Date().toISOString();

    this.opts.onMessage('__tui_chat__', {
      id,
      chat_jid: '__tui_chat__',
      sender: 'user',
      sender_name: 'You',
      content: trimmed,
      timestamp,
      is_from_me: false,
      is_bot_message: false,
    });

    this.opts.onChatMetadata('__tui_chat__', timestamp, 'TUI Chat', 'tui', false);
    logger.info({ input: trimmed }, 'TUI input received');
  }

  async sendMessage(jid: string, text: string): Promise<void> {
    this.messageQueue.push(text);
    this.processQueue();
  }

  private async processQueue(): Promise<void> {
    if (this.isProcessing || this.messageQueue.length === 0) return;
    this.isProcessing = true;

    while (this.messageQueue.length > 0) {
      const message = this.messageQueue.shift();
      if (message) await this.displayMessage(message);
    }

    this.isProcessing = false;
  }

  private async displayMessage(message: string): Promise<void> {
    const cleanMessage = message.replace(/<internal>[\s\S]*?<\/internal>/g, '').trim();
    
    console.log('\n\x1b[32mNanoBob:\x1b[0m');
    const lines = this.wrapText(cleanMessage, 70);
    for (const line of lines) {
      console.log(`  ${line}`);
    }
    console.log();
  }

  private wrapText(text: string, width: number): string[] {
    const words = text.split(' ');
    const lines: string[] = [];
    let currentLine = '';

    for (const word of words) {
      if ((currentLine + word).length <= width) {
        currentLine += (currentLine ? ' ' : '') + word;
      } else {
        if (currentLine) lines.push(currentLine);
        currentLine = word;
      }
    }
    if (currentLine) lines.push(currentLine);
    return lines;
  }

  isConnected(): boolean {
    return this.connected;
  }

  ownsJid(jid: string): boolean {
    return jid === '__tui_chat__';
  }

  async disconnect(): Promise<void> {
    this.connected = false;
    if (this.rl) this.rl.close();
    logger.info('TUI channel disconnected');
    console.log('\nGoodbye!\n');
    process.exit(0);
  }

  async setTyping(jid: string, isTyping: boolean): Promise<void> {
    if (isTyping) {
      process.stdout.write('\r\x1b[33mNanoBob is typing...\x1b[0m\x1b[K');
    } else {
      process.stdout.write('\r\x1b[K');
    }
  }
}

registerChannel('tui', (opts: ChannelOpts) => {
  return new TUIChannel(opts);
});
