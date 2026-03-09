# /add-telegram - Telegram Channel Skill

## Purpose
Add Telegram as a communication channel for NanoBob.

## Prerequisites
- Telegram Bot Token from [@BotFather](https://t.me/botfather)

## What This Skill Does
1. Creates `src/channels/telegram.ts` with Telegram channel implementation
2. Adds import to `src/channels/index.ts`
3. Updates `.env` with `TELEGRAM_BOT_TOKEN`
4. Rebuilds the project

## Usage
Inside the `claude` CLI, run:
```
/add-telegram
```

Then follow prompts to:
1. Enter your Telegram Bot Token
2. Test the connection
3. Register groups from Telegram chats

## Implementation Details

### Channel File: `src/channels/telegram.ts`
```typescript
import { registerChannel, ChannelOpts } from './registry.js';
import { Telegraf } from 'telegraf';

export class TelegramChannel implements Channel {
  // Implementation using Telegraf library
  // Handles message reception and sending
  // Maps Telegram chat IDs to internal JIDs
}

registerChannel('telegram', (opts: ChannelOpts) => {
  const token = process.env.TELEGRAM_BOT_TOKEN;
  if (!token) return null;
  return new TelegramChannel(opts);
});
```

### Dependencies
Add to `package.json`:
```json
"telegraf": "^4.16.0"
```

### Environment Variable
```bash
TELEGRAM_BOT_TOKEN=your_bot_token_here
```

## Post-Installation
1. Run `npm install` to install new dependencies
2. Run `npm run build` to compile TypeScript
3. Restart NanoBob
4. Use `@Bob` in your Telegram chats
