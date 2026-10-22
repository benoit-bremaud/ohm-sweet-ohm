import { describe, expect, it, vi } from 'vitest';

import { idleConnectionErrorHandler } from './pool-error-handler.js';

describe('idleConnectionErrorHandler', () => {
  it('should log a pool error raised before the app exists', () => {
    const logger = { warn: vi.fn() };
    const onError = idleConnectionErrorHandler(logger);
    const error = new Error('connect ECONNREFUSED');

    onError(error);

    expect(logger.warn).toHaveBeenCalledWith(
      { err: error },
      'database connection lost; it reconnects on the next query',
    );
  });
});
