import { Channel } from './types.js';

export function findChannel(
  channels: Channel[],
  jid: string,
): Channel | undefined {
  return channels.find((ch) => ch.ownsJid(jid));
}

export function formatMessages(
  messages: Array<{
    sender_name?: string;
    sender: string;
    content: string;
    timestamp: string;
  }>,
  timezone: string,
): string {
  return messages
    .map((msg) => {
      const date = new Date(msg.timestamp);
      const timeStr = date.toLocaleTimeString('en-US', {
        timeZone: timezone,
        hour: 'numeric',
        minute: '2-digit',
        hour12: true,
      });
      const dateStr = date.toLocaleDateString('en-US', {
        timeZone: timezone,
        month: 'short',
        day: 'numeric',
      });
      const name = msg.sender_name || msg.sender;
      return `[${dateStr} ${timeStr}] ${name}: ${msg.content}`;
    })
    .join('\n');
}

export function formatOutbound(text: string): string {
  return text.trim();
}

export function escapeXml(text: string): string {
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&apos;');
}
