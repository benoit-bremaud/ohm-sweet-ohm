import { experimental_AstroContainer as AstroContainer } from 'astro/container';
import { beforeAll, describe, expect, it } from 'vitest';

import { LED_BLOCK } from '../lib/block.fixture';
import Breadcrumb from './Breadcrumb.astro';
import Formulas from './Formulas.astro';
import KeyComponents from './KeyComponents.astro';
import SafetyWarning from './SafetyWarning.astro';
import Schematic from './Schematic.astro';
import SpecTable from './SpecTable.astro';

const NBSP = ' ';

/** Matches a table row whose header is `label` and whose value cell holds `value`. */
const row = (label: string, value: string) =>
  new RegExp(`${label}</th>\\s*<td[^>]*>\\s*${value}\\s*</td>`);

let container: AstroContainer;

beforeAll(async () => {
  container = await AstroContainer.create();
});

describe('SpecTable', () => {
  it('shows every spec with its SI-prefixed unit, enum values capitalised', async () => {
    const html = await container.renderToString(SpecTable, { props: { specs: LED_BLOCK.specs } });

    expect(html).toMatch(row('Supply voltage', `5${NBSP}V`));
    expect(html).toMatch(row('LED current', `13.6${NBSP}mA`));
    expect(html).toMatch(row('LED colour', 'Red'));
    expect(html).toMatch(row('Number of LEDs', '1'));
  });

  it('says so when there is no spec', async () => {
    const html = await container.renderToString(SpecTable, { props: { specs: [] } });

    expect(html).toContain('no specification yet');
    expect(html).not.toContain('<table');
  });
});

describe('Schematic', () => {
  it('loads the drawing as an image from the given URL, never inline', async () => {
    const src = 'http://api.test/blocks/led-resistor-basic/schematic.svg';

    const html = await container.renderToString(Schematic, { props: { block: LED_BLOCK, src } });

    expect(html).toMatch(
      /<img[^>]+src="http:\/\/api\.test\/blocks\/led-resistor-basic\/schematic\.svg"/,
    );
    expect(html).toContain('alt="Schematic of LED with current-limiting resistor"');
    expect(html).not.toContain('<svg');
    expect(html).toContain('Theoretical');
    expect(html).toContain('Beginner');
  });

  it('labels a tested block as such', async () => {
    const html = await container.renderToString(Schematic, {
      props: { block: { ...LED_BLOCK, validationStatus: 'tested' }, src: 'http://api.test/x.svg' },
    });

    expect(html).toContain('Tested on a real build');
  });
});

describe('Breadcrumb', () => {
  it('renders nothing for a root block', async () => {
    const html = await container.renderToString(Breadcrumb, { props: { block: LED_BLOCK } });

    expect(html).not.toContain('<nav');
  });

  it('links each ancestor of a variant, the base circuit first', async () => {
    const variant = {
      ...LED_BLOCK,
      slug: 'led-resistor-two',
      path: [...LED_BLOCK.path, { slug: 'led-resistor-two', name: 'Two LEDs' }],
    };

    const html = await container.renderToString(Breadcrumb, { props: { block: variant } });

    expect(html).toMatch(/<ol[^>]*>\s*<li[^>]*>\s*LED with current-limiting resistor\s*<\/li>/);
    expect(html).toContain('href="/blocks/led-resistor-basic"');
    expect(html).not.toContain('href="/blocks/led-resistor-two"');
  });
});

describe('Formulas', () => {
  it('renders the expression as code', async () => {
    const html = await container.renderToString(Formulas, {
      props: { formulas: LED_BLOCK.formulas },
    });

    expect(html).toContain('<code');
    expect(html).toContain('R = (supplyVoltage − n·Vf) / ledCurrent');
  });

  it('has an empty state', async () => {
    const html = await container.renderToString(Formulas, { props: { formulas: [] } });

    expect(html).toContain('No design formula');
  });
});

describe('KeyComponents', () => {
  it('renders the part number and its role', async () => {
    const html = await container.renderToString(KeyComponents, {
      props: { components: [{ partNumber: 'LM317', role: 'regulator' }] },
    });

    expect(html).toContain('LM317');
    expect(html).toContain('regulator');
  });

  it('has an empty state', async () => {
    const html = await container.renderToString(KeyComponents, { props: { components: [] } });

    expect(html).toContain('no specific component');
  });
});

describe('SafetyWarning', () => {
  it('names the hazard', async () => {
    const html = await container.renderToString(SafetyWarning);

    expect(html).toContain('Hazardous voltage');
  });
});
