import { describe, expect, it, vi } from 'vitest';
import type { APIContext } from 'astro';

import { GET } from './index';

describe('GET /', () => {
  it('redirects temporarily to the troubleshooting guides', async () => {
    const redirect = vi.fn(
      (to: string, status: number) => new Response(null, { status, headers: { location: to } }),
    );

    const response = await GET({ redirect } as unknown as APIContext);

    expect(response.status).toBe(302);
    expect(response.headers.get('location')).toBe('/depannage/');
  });
});
