import { describe, expect, it, vi } from 'vitest';

import { LED_BLOCK } from './block.fixture';
import { fetchBlock, isSlug } from './catalogue-api';

const API = 'http://api.test';

function answering(status: number, body: string): typeof fetch {
  return vi.fn(() =>
    Promise.resolve(
      new Response(body, { status, headers: { 'content-type': 'application/json' } }),
    ),
  );
}

describe('isSlug', () => {
  it.each(['led-resistor-basic', 'a', 'v2'])('accepts %s', (slug) => {
    expect(isSlug(slug)).toBe(true);
  });

  it.each(['', 'Bad_Slug', '-led', 'led-', 'a/b', '../etc'])('rejects %j', (slug) => {
    expect(isSlug(slug)).toBe(false);
  });
});

describe('fetchBlock', () => {
  it('returns the block when the API answers a valid response', async () => {
    const fetchFn = answering(200, JSON.stringify(LED_BLOCK));

    const lookup = await fetchBlock(API, 'led-resistor-basic', fetchFn);

    expect(lookup).toEqual({ kind: 'found', block: LED_BLOCK });
    expect(fetchFn).toHaveBeenCalledWith(
      new URL('http://api.test/blocks/led-resistor-basic'),
      expect.objectContaining({ headers: { accept: 'application/json' } }),
    );
  });

  it('uses the origin of the API URL only', async () => {
    const fetchFn = answering(200, JSON.stringify(LED_BLOCK));

    await fetchBlock('http://api.test:8080/v1/', 'led', fetchFn);

    expect(fetchFn).toHaveBeenCalledWith(
      new URL('http://api.test:8080/blocks/led'),
      expect.anything(),
    );
  });

  it('never calls the API for a malformed slug', async () => {
    const fetchFn = answering(200, JSON.stringify(LED_BLOCK));

    const lookup = await fetchBlock(API, '../admin', fetchFn);

    expect(lookup).toEqual({ kind: 'not-found' });
    expect(fetchFn).not.toHaveBeenCalled();
  });

  it('reports an unknown block as not found', async () => {
    const lookup = await fetchBlock(API, 'nope', answering(404, '{"error":"no block"}'));

    expect(lookup).toEqual({ kind: 'not-found' });
  });

  it('reports a server error as unavailable, with the status for the logs', async () => {
    const lookup = await fetchBlock(API, 'led', answering(500, '{"error":"boom"}'));

    expect(lookup).toEqual({ kind: 'unavailable', reason: 'API answered 500' });
  });

  it('reports a network failure as unavailable', async () => {
    const fetchFn: typeof fetch = vi.fn(() => Promise.reject(new Error('ECONNREFUSED')));

    const lookup = await fetchBlock(API, 'led', fetchFn);

    expect(lookup).toEqual({ kind: 'unavailable', reason: 'API unreachable: ECONNREFUSED' });
  });

  it('reports a body that is not JSON as unavailable', async () => {
    const lookup = await fetchBlock(API, 'led', answering(200, '<html>'));

    expect(lookup).toMatchObject({
      kind: 'unavailable',
      reason: expect.stringContaining('not JSON') as string,
    });
  });

  it('refuses a response that drifts from the contract', async () => {
    const offContract = { ...LED_BLOCK, specs: [{ key: 'x', kind: 'colour' }] };

    const lookup = await fetchBlock(API, 'led', answering(200, JSON.stringify(offContract)));

    expect(lookup).toMatchObject({
      kind: 'unavailable',
      reason: expect.stringContaining('off contract') as string,
    });
  });

  it('refuses a source link that is not http(s), so no javascript: href reaches the page', async () => {
    const hostile = { ...LED_BLOCK, source: { title: 'x', url: 'javascript:alert(1)' } };

    const lookup = await fetchBlock(API, 'led', answering(200, JSON.stringify(hostile)));

    expect(lookup).toMatchObject({ kind: 'unavailable' });
  });
});
