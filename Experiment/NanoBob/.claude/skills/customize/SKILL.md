# /customize - NanoBob Customization Skill

## Purpose
Guided customization for adding channels, integrations, and changing behavior.

## Usage
Inside the `claude` CLI, run:
```
/customize
```

## Customization Options

### Change Assistant Name
```bash
# Edit src/config.ts or set env variable
ASSISTANT_NAME=YourName
```

### Add Communication Channels
Run channel skills:
- `/add-telegram` - Add Telegram bot
- `/add-whatsapp` - Add WhatsApp messaging
- `/add-slack` - Add Slack workspace
- `/add-discord` - Add Discord bot

### Configure Container Settings
```bash
# In .env:
CONTAINER_IMAGE=nanobob-agent:latest
CONTAINER_TIMEOUT=1800000
MAX_CONCURRENT_CONTAINERS=5
```

### Modify Response Behavior
Edit the system prompt in `container/agent-runner/src/index.ts`

### Add Custom Skills
Create new skill directories under `.claude/skills/`

## Philosophy
NanoBob doesn't use configuration files for core behavior.
Instead, modify the code directly - the codebase is small enough
to understand and safe to change.
