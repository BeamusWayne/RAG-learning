import { ChildProcess } from 'child_process';
import { logger } from './logger.js';

interface QueuedMessage {
  chatJid: string;
  prompt: string;
}

interface ProcessInfo {
  proc: ChildProcess;
  containerName: string;
  groupFolder: string;
}

export class GroupQueue {
  private queue: QueuedMessage[] = [];
  private activeProcesses: Map<string, ProcessInfo> = new Map();
  private processMessagesFn?: (chatJid: string) => Promise<boolean>;
  private processingGroups: Set<string> = new Set();

  enqueueMessageCheck(chatJid: string): boolean {
    logger.debug({ chatJid }, 'Enqueueing message check');
    // For non-container channels (like TUI), process immediately
    if (this.processMessagesFn && !this.processingGroups.has(chatJid)) {
      this.processingGroups.add(chatJid);
      this.processMessagesFn(chatJid).then(() => {
        this.processingGroups.delete(chatJid);
      }).catch((err) => {
        logger.error({ err, chatJid }, 'Error processing messages');
        this.processingGroups.delete(chatJid);
      });
    }
    return true;
  }

  sendMessage(chatJid: string, prompt: string): boolean {
    const proc = this.activeProcesses.get(chatJid);
    if (!proc) {
      // No container - process immediately for non-container channels
      this.enqueueMessageCheck(chatJid);
      return true;
    }
    this.queue.push({ chatJid, prompt });
    return true;
  }

  registerProcess(chatJid: string, proc: ChildProcess, containerName: string, groupFolder: string): void {
    this.activeProcesses.set(chatJid, { proc, containerName, groupFolder });
    logger.info({ chatJid, containerName }, 'Process registered');
  }

  closeStdin(chatJid: string): void {
    const proc = this.activeProcesses.get(chatJid);
    if (proc && proc.proc.stdin) {
      proc.proc.stdin.end();
      logger.debug({ chatJid }, 'Closed stdin for container');
    }
  }

  notifyIdle(chatJid: string): void {
    logger.debug({ chatJid }, 'Container notified as idle');
  }

  setProcessMessagesFn(fn: (chatJid: string) => Promise<boolean>): void {
    this.processMessagesFn = fn;
  }

  async shutdown(timeout: number): Promise<void> {
    logger.info('Shutting down group queue...');
    const promises: Promise<void>[] = [];

    for (const [jid, procInfo] of this.activeProcesses) {
      promises.push(
        new Promise((resolve) => {
          const timer = setTimeout(() => {
            procInfo.proc.kill('SIGKILL');
            logger.warn({ jid }, 'Force killed container');
            resolve();
          }, timeout);

          procInfo.proc.on('exit', () => {
            clearTimeout(timer);
            logger.info({ jid }, 'Container exited');
            resolve();
          });

          procInfo.proc.kill('SIGTERM');
        }),
      );
    }

    await Promise.all(promises);
    this.activeProcesses.clear();
    logger.info('Group queue shutdown complete');
  }
}
