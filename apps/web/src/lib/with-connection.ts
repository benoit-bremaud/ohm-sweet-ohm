/** A database handle that can be closed (a Kysely instance in the Worker). */
export interface Closable {
  destroy(): Promise<void>;
}

/**
 * Opens a connection for one read and always closes it: a Worker cannot reuse a connection across
 * requests (ADR-0005). The read's own error is the one that propagates; a failure to close is only
 * reported, so it never hides it.
 */
export async function withConnection<D extends Closable, T>(
  open: () => D,
  read: (db: D) => Promise<T>,
  onCloseFailed: (error: unknown) => void,
): Promise<T> {
  const db = open();
  try {
    return await read(db);
  } finally {
    await db.destroy().catch(onCloseFailed);
  }
}
