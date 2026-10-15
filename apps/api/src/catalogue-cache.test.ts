import { describe, expect, it, vi } from 'vitest';

import { CatalogueCache } from './catalogue-cache.js';
import { makeCatalogue } from './test-catalogue.js';

function setup() {
  const clock = { now: 0 };
  const source = {
    version: 'v1',
    failing: false,
    loadCatalogue: vi.fn(() => Promise.resolve(makeCatalogue())),
    catalogueVersion: vi.fn(() => {
      return source.failing
        ? Promise.reject(new Error('database down'))
        : Promise.resolve(source.version);
    }),
  };
  const onCheckFailed = vi.fn();
  const cache = new CatalogueCache(source, {
    checkIntervalMs: 5_000,
    now: () => clock.now,
    onCheckFailed,
  });
  return { clock, source, onCheckFailed, cache };
}

describe('CatalogueCache', () => {
  it('should not query the database again within the interval', async () => {
    const { clock, source, cache } = setup();

    await cache.get();
    clock.now = 4_999;
    await cache.get();

    expect(source.catalogueVersion).toHaveBeenCalledTimes(1);
    expect(source.loadCatalogue).toHaveBeenCalledTimes(1);
  });

  it('should only check the version after the interval when nothing was imported', async () => {
    const { clock, source, cache } = setup();
    const first = await cache.get();

    clock.now = 5_000;
    const second = await cache.get();

    expect(source.catalogueVersion).toHaveBeenCalledTimes(2);
    expect(source.loadCatalogue).toHaveBeenCalledTimes(1);
    expect(second).toBe(first);
  });

  it('should reload the catalogue when the version changed', async () => {
    const { clock, source, cache } = setup();
    const first = await cache.get();

    source.version = 'v2';
    clock.now = 5_000;
    const second = await cache.get();

    expect(source.loadCatalogue).toHaveBeenCalledTimes(2);
    expect(second).not.toBe(first);
  });

  it('should keep serving the cached catalogue when the check fails, and retry next interval', async () => {
    const { clock, source, onCheckFailed, cache } = setup();
    const first = await cache.get();

    source.failing = true;
    clock.now = 5_000;
    const duringOutage = await cache.get();
    clock.now = 6_000;
    await cache.get();

    expect(duringOutage).toBe(first);
    expect(onCheckFailed).toHaveBeenCalledTimes(1);
    expect(source.catalogueVersion).toHaveBeenCalledTimes(2);
  });

  it('should fail when the very first load fails, then recover', async () => {
    const { source, cache } = setup();
    source.failing = true;

    await expect(cache.get()).rejects.toThrow('database down');
    source.failing = false;

    await expect(cache.get()).resolves.toBeDefined();
  });

  it('should share one refresh between concurrent requests', async () => {
    const { source, cache } = setup();

    const [a, b] = await Promise.all([cache.get(), cache.get()]);

    expect(a).toBe(b);
    expect(source.catalogueVersion).toHaveBeenCalledTimes(1);
    expect(source.loadCatalogue).toHaveBeenCalledTimes(1);
  });
});
