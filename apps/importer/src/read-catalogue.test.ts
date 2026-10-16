import { describe, expect, it } from 'vitest';

import { byCodeUnit } from './read-catalogue.js';

describe('byCodeUnit', () => {
  it('orders like a bare sort, uppercase before lowercase, whatever the locale', () => {
    const names = ['led-b', 'LED-a', 'é', 'led-a', 'Zener', 'led-a'];
    expect(names.sort(byCodeUnit)).toEqual(['LED-a', 'Zener', 'led-a', 'led-a', 'led-b', 'é']);
    expect(byCodeUnit('a', 'a')).toBe(0);
  });
});
