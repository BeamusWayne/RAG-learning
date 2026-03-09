import Database from 'better-sqlite3';
import path from 'path';

import { STORE_DIR } from './config.js';
import { logger } from './logger.js';
import { NewMessage, RegisteredGroup, ScheduledTask } from './types.js';

let db: Database.Database | null = null;

export function initDatabase(): void {
  const dbPath = path.join(STORE_DIR, 'messages.db');
  db = new Database(dbPath);
  db.pragma('journal_mode = WAL');

  db.exec(`
    CREATE TABLE IF NOT EXISTS messages (
      id TEXT PRIMARY KEY,
      chat_jid TEXT NOT NULL,
      sender TEXT NOT NULL,
      sender_name TEXT,
      content TEXT NOT NULL,
      timestamp TEXT NOT NULL,
      is_from_me INTEGER NOT NULL,
      is_bot_message INTEGER DEFAULT 0,
      created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS chats (
      jid TEXT PRIMARY KEY,
      name TEXT,
      channel TEXT,
      is_group INTEGER DEFAULT 0,
      last_message_time TEXT,
      updated_at TEXT DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS registered_groups (
      jid TEXT PRIMARY KEY,
      name TEXT NOT NULL,
      folder TEXT NOT NULL,
      is_main INTEGER DEFAULT 0,
      requires_trigger INTEGER DEFAULT 1,
      added_at TEXT NOT NULL,
      container_config TEXT
    );

    CREATE TABLE IF NOT EXISTS sessions (
      group_folder TEXT PRIMARY KEY,
      session_id TEXT NOT NULL,
      updated_at TEXT DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS scheduled_tasks (
      id TEXT PRIMARY KEY,
      group_folder TEXT NOT NULL,
      prompt TEXT NOT NULL,
      schedule_type TEXT NOT NULL,
      schedule_value TEXT NOT NULL,
      status TEXT DEFAULT 'active',
      next_run TEXT,
      created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS task_run_logs (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      task_id TEXT NOT NULL,
      run_at TEXT DEFAULT CURRENT_TIMESTAMP,
      status TEXT,
      output TEXT
    );

    CREATE TABLE IF NOT EXISTS router_state (
      key TEXT PRIMARY KEY,
      value TEXT NOT NULL,
      updated_at TEXT DEFAULT CURRENT_TIMESTAMP
    );

    CREATE INDEX IF NOT EXISTS idx_messages_chat_jid ON messages(chat_jid);
    CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON messages(timestamp);
    CREATE INDEX IF NOT EXISTS idx_tasks_group_folder ON scheduled_tasks(group_folder);
    CREATE INDEX IF NOT EXISTS idx_tasks_status ON scheduled_tasks(status);
  `);

  logger.info('Database initialized');
}

export function storeMessage(msg: NewMessage): void {
  if (!db) throw new Error('Database not initialized');
  const stmt = db.prepare(`
    INSERT OR REPLACE INTO messages 
    (id, chat_jid, sender, sender_name, content, timestamp, is_from_me, is_bot_message)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
  `);
  stmt.run(
    msg.id,
    msg.chat_jid,
    msg.sender,
    msg.sender_name || null,
    msg.content,
    msg.timestamp,
    msg.is_from_me ? 1 : 0,
    msg.is_bot_message ? 1 : 0,
  );
}

export function storeChatMetadata(
  chatJid: string,
  timestamp: string,
  name?: string,
  channel?: string,
  isGroup?: boolean,
): void {
  if (!db) throw new Error('Database not initialized');
  const stmt = db.prepare(`
    INSERT OR REPLACE INTO chats (jid, name, channel, is_group, last_message_time, updated_at)
    VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
  `);
  stmt.run(
    chatJid,
    name || null,
    channel || null,
    isGroup ? 1 : 0,
    timestamp,
  );
}

export function getNewMessages(
  jids: string[],
  sinceTimestamp: string,
  assistantName: string,
): { messages: NewMessage[]; newTimestamp: string } {
  if (!db) throw new Error('Database not initialized');
  if (jids.length === 0) {
    return { messages: [], newTimestamp: sinceTimestamp };
  }

  const placeholders = jids.map(() => '?').join(',');
  const stmt = db.prepare(`
    SELECT id, chat_jid, sender, sender_name, content, timestamp, is_from_me, is_bot_message
    FROM messages
    WHERE chat_jid IN (${placeholders})
      AND timestamp > ?
      AND sender != ?
    ORDER BY timestamp ASC
  `);

  const rows = stmt.all(
    ...jids,
    sinceTimestamp,
    assistantName,
  ) as Array<{
    id: string;
    chat_jid: string;
    sender: string;
    sender_name: string | null;
    content: string;
    timestamp: string;
    is_from_me: number;
    is_bot_message: number;
  }>;

  const messages: NewMessage[] = rows.map((row) => ({
    ...row,
    sender_name: row.sender_name || undefined,
    is_from_me: row.is_from_me === 1,
    is_bot_message: row.is_bot_message === 1,
  }));

  const newTimestamp =
    messages.length > 0
      ? messages[messages.length - 1].timestamp
      : sinceTimestamp;

  return { messages, newTimestamp };
}

export function getMessagesSince(
  chatJid: string,
  sinceTimestamp: string,
  assistantName: string,
): NewMessage[] {
  if (!db) throw new Error('Database not initialized');
  const stmt = db.prepare(`
    SELECT id, chat_jid, sender, sender_name, content, timestamp, is_from_me, is_bot_message
    FROM messages
    WHERE chat_jid = ?
      AND timestamp > ?
      AND sender != ?
    ORDER BY timestamp ASC
  `);

  const rows = stmt.all(chatJid, sinceTimestamp, assistantName) as Array<{
    id: string;
    chat_jid: string;
    sender: string;
    sender_name: string | null;
    content: string;
    timestamp: string;
    is_from_me: number;
    is_bot_message: number;
  }>;

  return rows.map((row) => ({
    ...row,
    sender_name: row.sender_name || undefined,
    is_from_me: row.is_from_me === 1,
    is_bot_message: row.is_bot_message === 1,
  }));
}

export function getAllChats(): Array<{
  jid: string;
  name: string;
  channel: string;
  is_group: boolean;
  last_message_time: string;
}> {
  if (!db) throw new Error('Database not initialized');
  const stmt = db.prepare('SELECT * FROM chats ORDER BY last_message_time DESC');
  const rows = stmt.all() as Array<{
    jid: string;
    name: string;
    channel: string;
    is_group: number;
    last_message_time: string;
  }>;
  return rows.map((row) => ({
    ...row,
    is_group: row.is_group === 1,
  }));
}

export function getAllRegisteredGroups(): Record<string, RegisteredGroup> {
  if (!db) throw new Error('Database not initialized');
  const stmt = db.prepare('SELECT * FROM registered_groups');
  const rows = stmt.all() as Array<{
    jid: string;
    name: string;
    folder: string;
    is_main: number;
    requires_trigger: number;
    added_at: string;
    container_config: string | null;
  }>;

  const result: Record<string, RegisteredGroup> = {};
  for (const row of rows) {
    result[row.jid] = {
      name: row.name,
      folder: row.folder,
      isMain: row.is_main === 1,
      requiresTrigger: row.requires_trigger === 1,
      added_at: row.added_at,
      containerConfig: row.container_config
        ? JSON.parse(row.container_config)
        : undefined,
    };
  }
  return result;
}

export function setRegisteredGroup(
  jid: string,
  group: RegisteredGroup,
): void {
  if (!db) throw new Error('Database not initialized');
  const stmt = db.prepare(`
    INSERT OR REPLACE INTO registered_groups 
    (jid, name, folder, is_main, requires_trigger, added_at, container_config)
    VALUES (?, ?, ?, ?, ?, ?, ?)
  `);
  stmt.run(
    jid,
    group.name,
    group.folder,
    group.isMain ? 1 : 0,
    group.requiresTrigger !== false ? 1 : 0,
    group.added_at,
    group.containerConfig ? JSON.stringify(group.containerConfig) : null,
  );
}

export function getAllSessions(): Record<string, string> {
  if (!db) throw new Error('Database not initialized');
  const stmt = db.prepare('SELECT group_folder, session_id FROM sessions');
  const rows = stmt.all() as Array<{ group_folder: string; session_id: string }>;
  const result: Record<string, string> = {};
  for (const row of rows) {
    result[row.group_folder] = row.session_id;
  }
  return result;
}

export function setSession(
  groupFolder: string,
  sessionId: string,
): void {
  if (!db) throw new Error('Database not initialized');
  const stmt = db.prepare(`
    INSERT OR REPLACE INTO sessions (group_folder, session_id, updated_at)
    VALUES (?, ?, CURRENT_TIMESTAMP)
  `);
  stmt.run(groupFolder, sessionId);
}

export function getRouterState(key: string): string | null {
  if (!db) throw new Error('Database not initialized');
  const stmt = db.prepare('SELECT value FROM router_state WHERE key = ?');
  const row = stmt.get(key) as { value: string } | undefined;
  return row?.value || null;
}

export function setRouterState(key: string, value: string): void {
  if (!db) throw new Error('Database not initialized');
  const stmt = db.prepare(`
    INSERT OR REPLACE INTO router_state (key, value, updated_at)
    VALUES (?, ?, CURRENT_TIMESTAMP)
  `);
  stmt.run(key, value);
}

export function getAllTasks(): ScheduledTask[] {
  if (!db) throw new Error('Database not initialized');
  const stmt = db.prepare('SELECT * FROM scheduled_tasks ORDER BY created_at DESC');
  const rows = stmt.all() as ScheduledTask[];
  return rows;
}

export function insertTask(task: ScheduledTask): void {
  if (!db) throw new Error('Database not initialized');
  const stmt = db.prepare(`
    INSERT INTO scheduled_tasks 
    (id, group_folder, prompt, schedule_type, schedule_value, status, next_run)
    VALUES (?, ?, ?, ?, ?, ?, ?)
  `);
  stmt.run(
    task.id,
    task.group_folder,
    task.prompt,
    task.schedule_type,
    task.schedule_value,
    task.status,
    task.next_run || null,
  );
}

export function updateTaskStatus(id: string, status: string): void {
  if (!db) throw new Error('Database not initialized');
  const stmt = db.prepare(`
    UPDATE scheduled_tasks SET status = ? WHERE id = ?
  `);
  stmt.run(status, id);
}

export function deleteTask(id: string): void {
  if (!db) throw new Error('Database not initialized');
  const stmt = db.prepare('DELETE FROM scheduled_tasks WHERE id = ?');
  stmt.run(id);
}
