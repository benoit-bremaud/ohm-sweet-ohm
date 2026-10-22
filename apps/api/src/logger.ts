import type { FastifyBaseLogger } from 'fastify';

/**
 * Builds the pool's idle-connection error callback around a logger that exists before the app,
 * so an error raised while buildApp is still running is logged instead of throwing (#27).
 */
export function idleConnectionErrorHandler(
  logger: Pick<FastifyBaseLogger, 'warn'>,
): (error: Error) => void {
  return (error) => {
    logger.warn({ err: error }, 'database connection lost; it reconnects on the next query');
  };
}
