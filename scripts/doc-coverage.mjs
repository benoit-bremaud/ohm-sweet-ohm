// Documentation coverage of the production TypeScript: share of exported declarations that carry a
// doc block right above them. Presence only; quality stays with the doc-auditor review.
// Only a `/**` block on the line right above `export` counts.
// Bare re-exports and `type X = (typeof X)[keyof typeof X]` companions are not counted (doc-noise).
// Usage: node scripts/doc-coverage.mjs [floor-percent], exit 1 below the floor (default 90).
/* global console, process */
import { execFileSync } from 'node:child_process';
import { readFileSync } from 'node:fs';

const floor = Number(process.argv[2] ?? 90);
if (!Number.isFinite(floor)) {
  console.error(`doc coverage: invalid floor "${process.argv[2]}"`);
  process.exit(2);
}
const files = execFileSync(
  'git',
  ['ls-files', ':(glob)apps/*/src/**/*.ts', ':(glob)packages/*/src/**/*.ts'],
  { encoding: 'utf8' },
)
  .split('\n')
  .filter((f) => f && !f.endsWith('.test.ts') && !f.endsWith('.d.ts'));

const ignored = /^export\s+(\*|\{|type\s+\{)|^export\s+type\s+\w+\s*=\s*\(typeof\s/;
let total = 0;
const missing = [];
for (const file of files) {
  let previous = '';
  let inDocBlock = false;
  let lastBlockIsDoc = false;
  readFileSync(file, 'utf8')
    .split('\n')
    .forEach((line, index) => {
      if (line.startsWith('export ') && !ignored.test(line)) {
        total++;
        if (!(previous.trimEnd().endsWith('*/') && lastBlockIsDoc)) {
          missing.push(`${file}:${index + 1}`);
        }
      }
      const trimmed = line.trim();
      if (trimmed.startsWith('/*')) inDocBlock = trimmed.startsWith('/**');
      if (trimmed.endsWith('*/')) lastBlockIsDoc = inDocBlock;
      if (trimmed !== '') previous = line;
    });
}

const percent = total === 0 ? 100 : ((total - missing.length) / total) * 100;
for (const location of missing) console.log(`undocumented: ${location}`);
console.log(
  `doc coverage: ${percent.toFixed(1)} % (${total - missing.length}/${total}), floor ${floor} %`,
);
if (percent < floor) process.exit(1);
