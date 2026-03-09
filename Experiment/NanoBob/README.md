<p align="center">
  <img src="assets/nanobob-logo.png" alt="NanoBob" width="400">
</p>

<p align="center">
  An AI assistant powered by Qwen that runs agents securely in their own containers. 
  Lightweight, built to be easily understood and completely customized for your needs.
</p>

<p align="center">
  <a href="https://github.com/qwibitai/nanobob">nanobob.dev</a>&nbsp; • &nbsp;
  <a href="README_zh.md">中文</a>&nbsp; • &nbsp;
  <a href="https://discord.gg/VDdww8qS42"><img src="https://img.shields.io/discord/1470188214710046894?label=Discord&logo=discord&v=2" alt="Discord" valign="middle"></a>
</p>

Using Qwen Agent SDK, NanoBob can dynamically rewrite its code to customize its feature set for your needs.

## Why I Built NanoBob

NanoClaw is an impressive project, but it's tied to Claude. NanoBob provides the same core functionality, 
but powered by Qwen models through the DashScope API.

NanoBob provides that same core functionality, but in a codebase small enough to understand: 
one process and a few files. Agents run in their own Linux containers with filesystem isolation.

## Quick Start

```bash
git clone https://github.com/qwibitai/nanobob.git
cd nanobob
claude
```

Then run `/setup`. Claude Code handles everything: dependencies, authentication, container setup and service configuration.

> **Note:** Commands prefixed with `/` (like `/setup`, `/add-whatsapp`) are [Claude Code skills](https://code.claude.com/docs/en/skills). 
> Type them inside the `claude` CLI prompt, not in your regular terminal.

## Philosophy

**Small enough to understand.** One process, a few source files and no microservices. 
If you want to understand the full NanoBob codebase, just ask Claude Code to walk you through it.

**Secure by isolation.** Agents run in Linux containers and they can only see what's explicitly mounted. 
Bash access is safe because commands run inside the container, not on your host.

**Built for the individual user.** NanoBob isn't a monolithic framework; it's software that fits each user's exact needs. 
Instead of becoming bloatware, NanoBob is designed to be bespoke.

**Customization = code changes.** No configuration sprawl. Want different behavior? Modify the code. 
The codebase is small enough that it's safe to make changes.

**AI-native.**
- No installation wizard; Claude Code guides setup.
- No monitoring dashboard; ask Claude what's happening.
- No debugging tools; describe the problem and Claude fixes it.

**Skills over features.** Instead of adding features to the codebase, contributors submit 
[claude code skills](https://code.claude.com/docs/en/skills) like `/add-telegram` that transform your fork.

**Best harness, best model.** NanoBob runs on Qwen models via DashScope API, 
with the same architecture that makes NanoClaw powerful.

## What It Supports

- **Multi-channel messaging** - Talk to your assistant from WhatsApp, Telegram, Discord, Slack, or Gmail. 
  Add channels with skills like `/add-whatsapp` or `/add-telegram`.
- **Isolated group context** - Each group has its own memory, isolated filesystem, 
  and runs in its own container sandbox.
- **Main channel** - Your private channel (self-chat) for admin control.
- **Scheduled tasks** - Recurring jobs that run Qwen and can message you back.
- **Web access** - Search and fetch content from the Web.
- **Container isolation** - Agents are sandboxed in Docker containers.

## Usage

Talk to your assistant with the trigger word (default: `@Bob`):

```
@Bob send an overview of the sales pipeline every weekday morning at 9am
@Bob review the git history for the past week each Friday and update the README
@Bob every Monday at 8am, compile news on AI developments and message me a briefing
```

From the main channel (your self-chat), you can manage groups and tasks:
```
@Bob list all scheduled tasks across groups
@Bob pause the Monday briefing task
@Bob join the Family Chat group
```

## Customizing

NanoBob doesn't use configuration files. To make changes, just tell Claude Code what you want:

- "Change the trigger word to @Assistant"
- "Remember in the future to make responses shorter"
- "Add a custom greeting when I say good morning"

Or run `/customize` for guided changes.

## Contributing

**Don't add features. Add skills.**

If you want to add Telegram support, don't create a PR that adds Telegram alongside WhatsApp. 
Instead, contribute a skill file (`.claude/skills/add-telegram/SKILL.md`) that teaches Claude Code 
how to transform a NanoBob installation to use Telegram.

### RFS (Request for Skills)

Skills we'd like to see:

**Communication Channels**
- `/add-signal` - Add Signal as a channel
- `/add-wechat` - Add WeChat integration

**Session Management**
- `/clear` - Add a `/clear` command that compacts the conversation

## Requirements

- macOS or Linux
- Node.js 20+
- [Claude Code](https://claude.ai/download)
- [Docker](https://docker.com/products/docker-desktop) (macOS/Linux)

## Architecture

```
Channels --> SQLite --> Polling loop --> Container (Qwen Agent) --> Response
```

Single Node.js process. Channels self-register at startup. 
Agents execute in isolated Linux containers with filesystem isolation.

Key files:
- `src/index.ts` - Orchestrator: state, message loop, agent invocation
- `src/channels/registry.ts` - Channel registry
- `src/db.ts` - SQLite operations
- `src/container-runner.ts` - Spawns streaming agent containers
- `container/` - Qwen agent runner

## FAQ

**Can I use other models?**

Yes. NanoBob supports any OpenAI-compatible API endpoint. Set these environment variables:

```bash
DASHSCOPE_BASE_URL=https://your-api-endpoint.com
DASHSCOPE_API_KEY=your-token-here
```

This allows you to use:
- Qwen models via DashScope
- Other models via compatible APIs

**Is this secure?**

Agents run in containers, not behind application-level permission checks. 
They can only access explicitly mounted directories.

**How do I debug issues?**

Ask Claude Code. "Why isn't the scheduler running?" "What's in the recent logs?" 
That's the AI-native approach that underlies NanoBob.

## Community

Questions? Ideas? [Join the Discord](https://discord.gg/VDdww8qS42).

## License

MIT
