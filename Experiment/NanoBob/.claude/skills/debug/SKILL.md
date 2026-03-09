# /debug - NanoBob Debugging Skill

## Purpose
Container debugging, log analysis, and troubleshooting.

## Usage
Inside the `claude` CLI, run:
```
/debug
```

## Common Issues

### Container Not Starting
```bash
# Check container runtime
docker ps
# or for Apple Container
container list

# Rebuild container
./container/build.sh
```

### Messages Not Processing
```bash
# Check logs
tail -f logs/nanobob.log

# Check database
sqlite3 store/messages.db "SELECT * FROM messages ORDER BY timestamp DESC LIMIT 10;"

# Check registered groups
sqlite3 store/messages.db "SELECT * FROM registered_groups;"
```

### Channel Connection Issues
```bash
# Verify credentials in .env
# Check channel-specific logs
```

### Database Corruption
```bash
# Backup and reset
cp store/messages.db store/messages.db.backup
# Then restart NanoBob
```

## Log Locations
- Host logs: `logs/nanobob.log`, `logs/nanobob.error.log`
- Container logs: `groups/{folder}/logs/container-*.log`
- IPC messages: `data/ipc/messages/`

## Recovery Mode
To recover from a crash:
1. Check for orphaned containers: `docker ps | grep nanobob`
2. Clean up: Remove orphaned containers
3. Run recovery: NanoBob auto-recovers pending messages on startup
