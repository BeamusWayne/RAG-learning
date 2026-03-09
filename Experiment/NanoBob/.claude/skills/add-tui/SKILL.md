# /add-tui - TUI Channel Skill

## Purpose
Add a Terminal User Interface (TUI) channel for direct terminal communication with NanoBob.

## What This Skill Does
1. Creates `src/channels/tui.ts` with TUI channel implementation
2. Adds import to `src/channels/index.ts`
3. Adds `ink` and `@inkjs/ui` dependencies
4. Enables interactive terminal chat

## Usage
Inside the `claude` CLI, run:
```
/add-tui
```

Then run:
```bash
npm run tui
```

## Implementation

### Channel File: `src/channels/tui.ts`
```typescript
import { registerChannel, ChannelOpts } from './registry.js';
import { render, Text, useInput, useApp } from 'ink';
import React, { useState, useEffect } from 'react';

export class TUIChannel implements Channel {
  // Handles terminal input/output
  // Displays messages in terminal
}

registerChannel('tui', (opts) => {
  return new TUIChannel(opts);
});
```

### New Script
Add to `package.json`:
```json
"tui": "tsx src/tui-main.ts"
```

## Post-Installation
1. Run `npm install`
2. Run `npm run tui` to start interactive terminal chat
