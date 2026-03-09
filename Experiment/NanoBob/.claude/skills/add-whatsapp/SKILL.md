# /add-whatsapp - WhatsApp Channel Skill

## Purpose
Add WhatsApp as a communication channel for NanoBob.

## Prerequisites
- WhatsApp phone number for the bot
- Ability to scan QR code for authentication

## What This Skill Does
1. Creates `src/channels/whatsapp.ts` with WhatsApp channel implementation
2. Adds import to `src/channels/index.ts`
3. Sets up authentication flow using Baileys library
4. Creates authentication storage in `store/auth/`

## Usage
Inside the `claude` CLI, run:
```
/add-whatsapp
```

Then follow prompts to:
1. Enter the WhatsApp number for the bot
2. Scan the QR code displayed
3. Wait for authentication to complete
4. Register WhatsApp groups

## Implementation Details

### Channel File: `src/channels/whatsapp.ts`
```typescript
import { registerChannel, ChannelOpts } from './registry.js';
import makeWASocket from '@whiskeysockets/baileys';

export class WhatsAppChannel implements Channel {
  // Implementation using Baileys library
  // Handles WhatsApp message reception and sending
  // Manages authentication state
}

registerChannel('whatsapp', (opts: ChannelOpts) => {
  // Check for auth credentials
  return new WhatsAppChannel(opts);
});
```

### Dependencies
Add to `package.json`:
```json
"@whiskeysockets/baileys": "^6.7.0"
```

### Authentication
Credentials stored in `store/auth/whatsapp.json`

## Post-Installation
1. Run `npm install` to install new dependencies
2. Run `npm run build` to compile TypeScript
3. Run authentication flow
4. Restart NanoBob
5. Use `@Bob` in your WhatsApp chats
