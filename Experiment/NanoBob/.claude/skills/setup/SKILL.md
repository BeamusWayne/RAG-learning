# /setup - NanoBob Setup Skill

## Purpose
First-time installation, authentication, and service configuration for NanoBob.

## What This Skill Does
1. Verifies Node.js 20+ is installed
2. Installs npm dependencies
3. Creates `.env` from `.env.example`
4. Guides user through Qwen API authentication
5. Builds the container image
6. Creates initial group folders
7. Optionally configures system service (launchd/systemd)

## Usage
Inside the `claude` CLI, run:
```
/setup
```

## Steps

### 1. Check Prerequisites
- Node.js 20+ (`node --version`)
- Docker or Apple Container runtime
- Git (for cloning if needed)

### 2. Install Dependencies
```bash
npm install
```

### 3. Setup Environment
```bash
cp .env.example .env
```

Then guide user to set:
- `DASHSCOPE_API_KEY` - Qwen API key
- `ASSISTANT_NAME` - Default: Bob

### 4. Build Container
```bash
./container/build.sh
```

### 5. Create Initial Folders
```bash
mkdir -p groups/global
mkdir -p groups/qwen_main/logs
mkdir -p store data/sessions data/env data/ipc/{messages,tasks,input} logs
```

### 6. Initialize Database
Run `npm run build` then `npm start` once to initialize SQLite.

### 7. Optional: System Service
Configure launchd (macOS) or systemd (Linux) for auto-start.

## Post-Setup
After setup completes, the user can:
- Talk to @Bob in connected channels
- Add more channels via skills like `/add-telegram`
- Create scheduled tasks
- Manage groups from the main channel
