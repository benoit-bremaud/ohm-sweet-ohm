import { describe, expect, it, vi } from 'vitest';

import { withConnection } from './with-connection';

function connection(destroy = vi.fn(() => Promise.resolve())) {
  return { destroy };
}

describe('withConnection', () => {
  it('returns the read result and closes the connection', async () => {
    const db = connection();

    const result = await withConnection(
      () => db,
      () => Promise.resolve(42),
      vi.fn(),
    );

    expect(result).toBe(42);
    expect(db.destroy).toHaveBeenCalledOnce();
  });

  it('closes the connection when the read fails and rethrows the read error', async () => {
    const db = connection();

    const reading = withConnection(
      () => db,
      () => Promise.reject(new Error('timeout')),
      vi.fn(),
    );

    await expect(reading).rejects.toThrow('timeout');
    expect(db.destroy).toHaveBeenCalledOnce();
  });

  it('keeps the read error when closing fails too, and reports the close failure', async () => {
    const closeError = new Error('socket closed');
    const db = connection(vi.fn(() => Promise.reject(closeError)));
    const onCloseFailed = vi.fn();

    const reading = withConnection(
      () => db,
      () => Promise.reject(new Error('timeout')),
      onCloseFailed,
    );

    await expect(reading).rejects.toThrow('timeout');
    expect(onCloseFailed).toHaveBeenCalledWith(closeError);
  });

  it('returns the result when only closing fails', async () => {
    const onCloseFailed = vi.fn();
    const db = connection(vi.fn(() => Promise.reject(new Error('socket closed'))));

    expect(
      await withConnection(
        () => db,
        () => Promise.resolve('ok'),
        onCloseFailed,
      ),
    ).toBe('ok');
    expect(onCloseFailed).toHaveBeenCalledOnce();
  });
});
