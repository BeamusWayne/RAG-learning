# NanoBob Specification

A personal Qwen assistant with multi-channel support, persistent memory per conversation, 
scheduled tasks, and container-isolated agent execution.

---

## Table of Contents

1. [Architecture](#architecture)
2. [Folder Structure](#folder-structure)
3. [Configuration](#configuration)
4. [Memory System](#memory-system)
5. [Session Management](#session-management)
6. [Message Flow](#message-flow)
7. [Scheduled Tasks](#scheduled-tasks)
8. [Security Considerations](#security-considerations)

---

## Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│                        HOST (macOS / Linux)                           │
│                     (Main Node.js Process)                            │
├──────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌──────────────────┐                  ┌────────────────────┐        │
│  │ Channels         │─────────────────▶│   SQLite Database  │        │
│  │ (self-register   │◀────────────────│   (messages.db)    │        │
│  │  at startup)     │  store/send      └─────────┬──────────┘        │
│  └──────────────────┘                            │                   │
│                                                   │                   │
│         ┌─────────────────────────────────────────┘                   │
│         │                                                             │
│         ▼                                                             │
│  ┌──────────────────┐    ┌──────────────────┐                         │
│  │  Message Loop    │    │  Scheduler Loop  │                         │
│  │  (polls SQLite)  │    │  (checks tasks)  │                         │
│  └────────┬─────────┘    └────────┬─────────┘                         │
│           │                       │                                   │
│           └───────────┬───────────┘                                   │
│                       │ spawns container                              │
│                       ▼                                               │
├──────────────────────────────────────────────────────────────────────┤
│                     CONTAINER (Linux VM)                               │
├──────────────────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────────────────┐    │
│  │                    QWEN AGENT                                 │    │
│  │                                                                │    │
│  │  Working directory: /workspace/group (mounted from host)       │    │
│  │  Volume mounts:                                                │    │
│  │    • groups/{name}/ → /workspace/group                         │    │
│  │    • groups/global/ → /workspace/global/                       │    │
│  │    • data/sessions/{group}/ → /workspace/sessions/             │    │
│  │                                                                │    │
│  │  Tools:                                                         │    │
│  │    • Bash (sandboxed in container)                             │    │
│  │    • File operations (read, write, edit)                       │    │
│  │    • Web search and fetch                                      │    │
│  │                                                                │    │
│  └──────────────────────────────────────────────────────────────┘    │
│                                                                       │
└───────────────────────────────────────────────────────────────────────┘
```

### Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| Channel System | Channel registry | Self-registering channels |
| Message Storage | SQLite (better-sqlite3) | Store messages for polling |
| Container Runtime | Docker | Isolated environments |
| Agent | OpenAI SDK (Qwen via DashScope) | Qwen model inference |
| Runtime | Node.js 20+ | Host process |

---

## Folder Structure

```
nanobob/
├── NANOBOB.md                     # Project context
├── docs/
│   └── SPEC.md                    # This specification
├── README.md                      # User documentation
├── package.json                   # Node.js dependencies
├── tsconfig.json                  # TypeScript configuration
├── .gitignore
│
├── src/
│   ├── index.ts                   # Orchestrator
│   ├── channels/
│   │   ├── registry.ts            # Channel factory registry
│   │   └── index.ts               # Barrel imports
│   ├── config.ts                  # Configuration constants
│   ├── types.ts                   # TypeScript interfaces
│   ├── logger.ts                  # Pino logger
│   ├── db.ts                      # SQLite database
│   ├── group-queue.ts             # Per-group queue
│   └── router.ts                  # Message routing
│
├── container/
│   ├── Dockerfile                 # Container image
│   ├── build.sh                   # Build script
│   └── agent-runner/              # Qwen agent runner
│       ├── package.json
│       └── src/index.ts           # Agent entry point
│
├── .claude/
│   └── skills/
│       ├── setup/SKILL.md
│       ├── customize/SKILL.md
│       ├── debug/SKILL.md
│       ├── add-telegram/SKILL.md
│       └── add-whatsapp/SKILL.md
│
├── groups/
│   ├── CLAUDE.md                  # Global memory
│   └── {channel}_{name}/          # Per-group folders
│       ├── CLAUDE.md              # Group memory
│       └── logs/                  # Task logs
│
├── store/                         # Local data
│   └── messages.db                # SQLite database
│
└── data/                          # Application state
    ├── sessions/                  # Session data
    └── ipc/                       # IPC files
```

---

## Configuration

Configuration constants are in `src/config.ts`:

```typescript
export const ASSISTANT_NAME = 'Bob';
export const POLL_INTERVAL = 2000;
export const CONTAINER_IMAGE = 'nanobob-agent:latest';
export const MAX_CONCURRENT_CONTAINERS = 5;
export const TRIGGER_PATTERN = /^@Bob\b/i;
```

### Environment Variables

| Variable | Purpose | Default |
|----------|---------|---------|
| `DASHSCOPE_API_KEY` | Qwen API authentication | Required |
| `DASHSCOPE_BASE_URL` | API endpoint | DashScope default |
| `ASSISTANT_NAME` | Assistant name | Bob |
| `CONTAINER_TIMEOUT` | Container timeout (ms) | 1800000 |

---

## Memory System

NanoBob uses a hierarchical memory system based on CLAUDE.md files.

### Memory Hierarchy

| Level | Location | Read By | Written By |
|-------|----------|---------|------------|
| Global | `groups/CLAUDE.md` | All groups | Main only |
| Group | `groups/{name}/CLAUDE.md` | That group | That group |
| Files | `groups/{name}/*.md` | That group | That group |

---

## Message Flow

1. User sends message via channel
2. Channel stores message in SQLite
3. Message loop polls SQLite (2s interval)
4. Router checks trigger pattern
5. Qwen agent processes messages
6. Response sent via channel

---

## Scheduled Tasks

Tasks run as full agents in their group's context.

### Schedule Types

| Type | Format | Example |
|------|--------|---------|
| cron | Cron expression | `0 9 * * 1` |
| interval | Milliseconds | `3600000` |
| once | ISO timestamp | `2024-12-25T09:00:00Z` |

---

## Security Considerations

1. **Container Isolation**: Agents run in Docker containers
2. **Filesystem Mounts**: Only explicitly mounted directories accessible
3. **Non-root User**: Container runs as non-root `node` user
4. **No Host Access**: Bash commands run inside container

For full security model, see docs/SECURITY.md.
