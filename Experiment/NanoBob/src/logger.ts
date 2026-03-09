import pino from 'pino';

// Start with info level for startup
const pretty = pino.transport({
  target: 'pino-pretty',
  options: {
    colorize: true,
    translateTime: 'SYS:standard',
    ignore: 'pid,hostname',
  },
});

export const logger = pino(pretty);

// Function to silence logger after startup
export function silenceLogger(): void {
  const silent = pino({ level: 'silent' });
  Object.assign(logger, silent);
}
